import csv
import os
from datetime import datetime
from collections import defaultdict

class Hospital:
# Central data warehouse class

	def __init__(self):
	# List of dicts
		self.encounters = []
		self.providers = []
		self.departments = []
		self.procedures = []
		self.notes = []
		
	
	# Data loading
	
	def load_all_data(self, data_dir = "./data"):
	# Load all CSV files into memory from the specified dir
		self.encounters = self._load_csv(os.path.join(data_dir, "encounters.csv"))
		self.providers = self._load_csv(os.path.join(data_dir, "providers.csv"))
		self.departments = self._load_csv(os.path.join(data_dir, "departments.csv"))
		self.procedures = self._load_csv(os.path.join(data_dir, "procedures.csv"))
		self.notes = self._load_csv(os.path.join(data_dir, "notes.csv"))

	@staticmethod
	def _load_csv(filepath):
	# Generic CSV loader
		rows = []
		if not os.path.exists(filepath):
			print(f"[Warning] File not found: {filepath}")
			return rows
		
		with open(filepath, "r", newline = "") as f:
			reader = csv.DictReader(f)
			for row in reader:
				rows.append(row)
		return rows
		
		
	# Data saving
	
	def save_encounters(self, filepath = "./data/encounters.csv"):
	# Write encounters list back to CSV
		self._save_csv(self.encounters, filepath)
		
	def save_notes(self, filepath = "./data/notes.csv"):
	# Write notes list back to CSV
		self._save_csv(self.notes, filepath)
		
	def save_procedures(self, filepath = "./data/procedures.csv"):
	# Write procedures list back to CSV
		self._save_csv(self.procedures, filepath)
		
	@staticmethod
	def _save_csv(data, filepath):
	# Generic CSV writer
		if not data:
			return
		os.makedirs(os.path.dirname(filepath), exist_ok = True)
		fieldnames = list(data[0].keys())
		with open(filepath, "w", newline = "") as f:
			writer = csv.DictWriter(f, fieldnames = fieldnames)
			writer.writeheader()
			writer.writerows(data)
			

	# Encounter helpers (add/remove patient cascading)
	
	def add_encounter(self, patient_id, provider_id, department_id, encounter_date, encounter_type):
	# Create and append a new encounter record
	
		existing_ids = {e["encounter_id"] for e in self.encounters}
		new_num = len(self.encounters) + 1
		while f"E{new_num}" in existing_ids:
			new_num += 1
			
		new_encounter = {
			"encounter_id": f"E{new_num}",
			"patient_id": patient_id,
			"provider_id": provider_id,
			"department_id": department_id,
			"encounter_date": encounter_date,
			"encounter_type": encounter_type
		}
		self.encounters.append(new_encounter)
		return new_encounter
	
	def remove_patient_records(self, patient_id):
	# Remove all encounters, procedures, and notes tied to a patient
		self.encounters = [e for e in self.encounters if e["patient_id"] != patient_id]
		self.procedures = [p for p in self.procedures if p["patient_id"] != patient_id]
		self.notes = [n for n in self.notes if n["patient_id"] != patient_id]
		
	
	# Clinician/Nurse actions
	
	def count_visits(self, date_str):
	# Counting total visits on a given date in form of YYYY-MM-DD
		per_patient = defaultdict(int)
		per_department = defaultdict(int)
		total = 0
		
		for enc in self.encounters:
			if enc["encounter_date"] == date_str:
				total += 1
				per_patient[enc["patient_id"]] += 1
				per_department[enc["department_id"]] += 1
				
		return total, dict(per_patient), dict(per_department)
		
	def view_note(self, patient_id, date_str):
	# Return a list of note dicts for a given patient on a given date
		results = []
		for note in self.notes:
			if (note["patient_id"] == patient_id and note["note_date"] == date_str):
				results.append(note)
		return results
		

	# Admin actions
	
	def count_encounters_per_patient(self):
	# Count encouners grouped by patient id. Return a dict sorted in desc order
		counts = defaultdict(int)
		for enc in self.encounters:
			counts[enc["patient_id"]] += 1
		return dict(sorted(counts.items(), key = lambda x: x[1], reverse = True))

	def count_encounters_per_department(self):
	# Count encouners grouped by department. Return a dict sorted in desc order
		dept_map = {d["department_id"]: d["name"] for d in self.departments}
		
		counts = defaultdict(int)
		for enc in self.encounters:
			dept_name = dept_map.get(enc["department_id"], enc["department_id"])
			counts[dept_name] += 1
		return dict(sorted(counts.items(), key = lambda x: x[1], reverse = True))
		
	def monitor_provider_workload(self):
	# Count encounters per provider, ranked descending. Return a list of tuples of provider_name, specialty, count
		
		# Build provider_id -> info lookup
		prov_map = {p["provider_id"]: (p["name"], p["specialty"]) for p in self.providers}
		
		counts = defaultdict(int)
		for enc in self.encounters:
			counts[enc["provider_id"]] += 1
			
		ranked = sorted(counts.items(), key = lambda x: x[1], reverse = True)
		results = []
		for prov_id, count in ranked:
			name, specialty = prov_map.get(prov_id, (prov_id, "Unknown"))
			results.append((name, specialty, count))
		return results
		
		
	# Management actions
	
	def monitor_department_revenue(self):
	# Compute total procedure costs generated by each department. Return a dict sorted desc
	
		# Map encounter_id -> department_id
		enc_dept = {e["encounter_id"]: e["department_id"] for e in self.encounters}
		
		# Map department_id -> name
		dept_map = {d["department_id"]: d["name"] for d in self.departments}
		
		revenue = defaultdict(float)
		for proc in self.procedures:
			dept_id = enc_dept.get(proc["encounter_id"], "Unknown")
			dept_name = dept_map.get(dept_id, dept_id)
			revenue[dept_name] += float(proc["cost"])
			
		return dict(sorted(revenue.items(), key = lambda x: x[1], reverse = True))
		
		
	# Stats (for clinician/nurse/admin generate_key_stats)
	
	def generate_key_stats(self, patients):
	# Generate summary stats from patient + encounter data. Return a formatted string for display.
		lines = []
		lines.append("=" * 45)
		lines.append(" KEY STATS REPORT ")
		lines.append("=" * 45)
		
		# Patient demographics
		total = len(patients)
		lines.append(f"\nTotal patients: {total}")
		
		if total > 0:
			ages = [p.age for p in patients.values()]
			lines.append(f"Avg. age: {sum(ages) / total:.1f}")
			lines.append(f"Age range: {min(ages)} - {max(ages)}")
			
			gender_counts = defaultdict(int)
			for p in patients.values():
				gender_counts[p.gender] += 1
			lines.append("\nGender distribution: ")
			for g, c in sorted(gender_counts.items()):
				lines.append(f"{g}: {c} ({c / total * 100:.1f}%)")
				
			bmis = [p.bmi for p in patients.values()]
			lines.append(f"\nAvg. BMI: {sum(bmis) / total:.1f}")
			
			a1cs = [p.a1c for p in patients.values() if p.a1c is not None]
			if a1cs:
				lines.append(f"\nAvg. A1C: {sum(a1cs) / len(a1cs):.1f}")
				
			smokers = sum(1 for p in patients.values() if p.smoking)
			lines.append(f"\nSmoking: {smokers} ({smokers / total * 100:.1f}%)")
			
			
		# Encounter summary
		lines.append(f"\nTotal Encounters: {len(self.encounters)}")
		
		type_counts = defaultdict(int)
		for e in self.encounters:
			type_counts[e["encounter_type"]] += 1
		lines.append("Encounter types: ")
		for t, c in sorted(type_counts.items()):
			lines.append(f"{t}: {c}")
			
			
		# Procedure summary
		lines.append(f"\nTotal Procedures: {len(self.procedures)}")
		if self.procedures:
			costs = [float(p["cost"]) for p in self.procedures]
			lines.append(f"Total cost:  ${sum(costs):,.2f}")
			lines.append(f"Avg. cost: ${sum(costs) / len(costs):,.2f}")
			
		lines.append("\n" + "=" * 45)
		return "\n".join(lines)
		
	@staticmethod
	def log_usage(username, role, actions, login_time, success, filepath = "./output/usage_log.csv"):
	# Append a usage record to usage_log.csv
		os.makedirs(os.path.dirname(filepath), exist_ok = True)
		file_exists = os.path.exists(filepath)
		
		with open(filepath, "a", newline = "") as f:
			writer = csv.writer(f)
			if not file_exists:
				writer.writerow(["username", "role", "login_time", "actions_performed", "login_status"])
			writer.writerow([username, role, login_time, "; ".join(actions) if actions else "N/A", "Success" if success else "Failed"])