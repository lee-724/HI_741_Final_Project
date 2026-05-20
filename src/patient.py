import csv
import os
import random

class Patient:
# Represents a single patient record and provides CRUD operations

	HEADERS = ["patient_id", "age", "gender", "bmi", "a1c", "bp_sys", "bp_dia", "smoking"]
	
	GENDER_OPTIONS = ["Male", "Female", "Non-binary"]
	
	
	# Constructor
	
	def __init__(self, patient_id, age, gender, bmi, a1c, bp_sys, bp_dia, smoking):
	# Initialize a patient instance
		self.patient_id = patient_id
		self.age = age
		self.gender = gender
		self.bmi = bmi
		self.a1c = a1c
		self.bp_sys = bp_sys
		self.bp_dia = bp_dia
		self.smoking = smoking
	
	def __repr__(self):
		return (f"Patient (id = {self.patient_id}, age = {self.age}, gender = {self.gender})")
		
		
	# Serialization helpers
	
	def to_dict(self):
	# Return patient data as an ordered dict matching CSV headers
		return {
			"patient_id": self.patient_id,
			"age": self.age,
			"gender": self.gender,
			"bmi": self.bmi,
			"a1c": self.a1c,
			"bp_sys": self.bp_sys,
			"bp_dia": self.bp_dia,
			"smoking": self.smoking
		}
		
	def to_display_string(self):
	# Return a human-readable string for UI display
		smoking_label = "Yes" if self.smoking else "No"
		a1c_label = self.a1c if self.a1c is not None else "N/A"
		return (
			f"Patient ID: {self.patient_id}\n"
			f"Age: {self.age}\n"
			f"Gender: {self.gender}\n"
			f"BMI: {self.bmi}\n"
			f"A1C: {a1c_label}\n"
			f"BP SYS: {self.bp_sys}\n"
			f"BP DIA: {self.bp_dia}\n"
			f"Smoking: {smoking_label}"
		)
		
	@staticmethod
	def load_patients(filepath = "./data/patients.csv"):
	# Read patient.csv and return a dict keypad by patient_id
		patients = {}
		if not os.path.exists(filepath):
			print(f"[Warning] Patient file not found: {filepath}")
			return patients
		
		with open(filepath, "r", newline = "") as f:
			reader = csv.DictReader(f)
			for row in reader:
				pid = row["patient_id"].strip()
				a1c_raw = row.get("a1c", "").strip()
				a1c = float(a1c_raw) if a1c_raw else None
				
				patients[pid] = Patient(
					patient_id = pid,
					age = int(row["age"]),
					gender = row["gender"].strip(),
					bmi = float(row["bmi"]),
					a1c = a1c,
					bp_sys = int(row["bp_sys"]),
					bp_dia = int(row["bp_dia"]),
					smoking = row["smoking"].strip().lower() == "true"
				)
		return patients
		
	@staticmethod
	def save_patients(patients, filepath = "./data/patients.csv"):
	# Write the current patients dict back to CSV
		os.makedirs(os.path.dirname(filepath), exist_ok = True)
		
		with open(filepath, "w", newline = "") as f:
			writer = csv.DictWriter(f, fieldnames = Patient.HEADERS)
			writer.writeheader()
			for patient in patients.values():
				row = patient.to_dict()
				# Write a1c as empty string if missing
				if row["a1c"] is None:
					row["a1c"] = ""
				writer.writerow(row)
				
	
	# CRUD Operations
	
	@staticmethod
	def add_patient(patient, patients):
		if patient.patient_id in patients:
			return ("exists", patients[patient.patient_id])
		
		patients[patient.patient_id] = patient
		return ("added", patient)
		
	@staticmethod
	def remove_patient(patient_id, patients):
		if patient_id in patients:
			del patients[patient_id]
			return True
		return False
		
	@staticmethod
	def retrieve_patient(patient_id, patients):
		return patients.get(patient_id, None)
		
		
	# Helpers
	
	@staticmethod
	def generate_unique_id(existing_ids, prefix = "P"):
		while True:
			suffix = random.randint(1000, 99999)
			new_id = f"{prefix}{suffix}"
			if new_id not in existing_ids:
				return new_id
	
	@staticmethod
	def validate_patient_input(age, bmi, a1c, bp_sys, bp_dia):
		errors = []
		
		# Age
		try:
			age_val = int(age)
			if age_val < 0 or age_val > 90:
				errors.append("Age must be between 0 and 90.")
		except ValueError:
			errors.append("Age must be a whole number.")
			
			
		# BMI
		try:
			bmi_val = float(bmi)
			if bmi_val < 12 or bmi_val > 23:
				errors.append("BMI must be between 12 and 23.")
		except ValueError:
			errors.append("BMI must be a number.")
			
		# A1C
		if a1c not in (None, "", "None"):
			try:
				a1c_val = float(a1c)
				if a1c_val < 4 or a1c_val > 17:
					errors.append("Age must be between 4.0 and 17.0.")
			except ValueError:
				errors.append("A1C must be a number or left blank.")
				
		# Systolic BP
		try:
			sys_val = int(bp_sys)
			if sys_val < 60 or sys_val > 180:
				errors.append("Systolic BP must be between 60 and 180.")
		except ValueError:
			errors.append("Systolic BP must be a whole number.")
			
		# Diastolic BP
		try:
			dia_val = int(bp_dia)
			if dia_val < 20 or sys_val > 120:
				errors.append("Diastolic BP must be between 20 and 120.")
		except ValueError:
			errors.append("Diastolic BP must be a whole number.")
			
		if errors:
			return (False, "\n".join(errors))
		return (True, "")