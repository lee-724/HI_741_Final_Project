import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import random
from src.user import User
from src.patient import Patient
from src.hospital import Hospital

class App:
# Tkinter-based UI controller for the Clinical Data Warehouse

	def __init__(self):
		self.root = tk.Tk()
		self.root.title("Clinical Data Warehouse")
		self.root.geometry("800x600")
		self.root.resizable(True, True)
				
		# Data
		self.users = User.load_credentials()
		self.current_user = None
		self.login_time = None
		self.actions_performed = []
		
		self.patients = Patient.load_patients()
		self.hospital = Hospital()
		self.hospital.load_all_data()
		
		# Map button labels to handler methods
		self.ACTION_MAP = {
			"Retrieve patient": self._on_retrieve_patient,
			"Add patient": self._on_add_patient,
			"Remove patient": self._on_remove_patient,
			"Count visits": self._on_count_visits,
			"View note": self._on_view_note,
			"Generate key stats": self._on_generate_stats,
			"Count encounters per patient": self._on_count_enc_per_patient,
			"Count encounters by department": self._on_count_enc_by_dept,
			"Monitor provider workload": self._on_monitor_workload,
			"Monitor department revenue": self._on_monitor_revenue,
			"Exit": self._on_exit
		}
		
	def run(self):
	# Show login screen and start the main loop
		self._show_login_screen()
		self.root.mainloop()
		
	
	# Screen: Login
	
	def _show_login_screen(self):
		self._clear_screen()
		
		frame = tk.Frame(self.root)
		frame.place(relx = .5, rely = .4, anchor = "center")
		
		tk.Label(frame, text = "Clinical Data Warehouse", font = ("Times New Roman", 18, "bold")).grid(row = 0, column = 0, columnspan = 2, pady = (0, 20))
		
		# Username
		tk.Label(frame, text = "Username: ", font = ("Times New Roman", 12)).grid(row = 1, column = 0, sticky = "e", padx = 5, pady = 5)
		self.entry_user = tk.Entry(frame, font = ("Times New Roman", 12), width = 25)
		self.entry_user.grid(row = 1, column = 1, padx = 5, pady = 5)
		
		# Password
		tk.Label(frame, text = "Password: ", font = ("Times New Roman", 12)).grid(row = 2, column = 0, sticky = "e", padx = 5, pady = 5)
		self.entry_pass = tk.Entry(frame, font = ("Times New Roman", 12), width = 25, show = "*")
		self.entry_pass.grid(row = 2, column = 1, padx = 5, pady = 5)
		
		# Login button
		tk.Button(frame, text = "Log In", font = ("Times New Roman", 12), width = 15, command = self._handle_login).grid(row = 3, column = 0, columnspan = 2, pady = 15)
		
	def _handle_login(self):
	# Authenticate user, success -> menu, fail -> alert
		username = self.entry_user.get().strip()
		password = self.entry_pass.get().strip()
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
		user = User.authenticate(username, password, self.users)
		
		if user is None:
			# Log the failed attempt
			Hospital.log_usage(username, "unknown", [], now, success = False)
			messagebox.showerror("Login Failed", "Invalid username or password.")
			return
			
		# Successful login
		self.current_user = user
		self.login_time = now
		self.actions_performed = []
		self._show_menu()
		
	
	# Screen: Main menu
	
	def _show_menu(self):
	# Display action buttons based on the current user's role
		self._clear_screen()
		
		frame = tk.Frame(self.root)
		frame.place(relx = .5, rely = .45, anchor = "center")
		
		tk.Label(frame, text = (f"Welcome, {self.current_user.username}. {self.current_user.role}"), font = ("Times New Roman", 16, "bold")).pack(pady = (0, 20))
		
		for action in self.current_user.get_allowed_actions():
			handler = self.ACTION_MAP.get(action)
			
			if handler:
				tk.Button(frame, text = action, font = ("Times New Roman", 12), width = 30, command = handler).pack(pady = 4)
				
				
	# Reusable UI helpers
	
	def _clear_screen(self):
		for widget in self.root.winfo_children():
			widget.destroy()
			
	def _make_back_button(self, parent):
	# Add a 'Back to menu' button
		tk.Button(parent, text = "<- Back to menu", font = ("Times New Roman", 10), command = self._show_menu).pack(side = "bottom", pady = 10)
		
	def _show_scrollable_result(self, title, content):
		self._clear_screen()
		
		frame = tk.Frame(self.root)
		frame.pack(fill = "both", expand = True, padx = 20, pady = 10)
		
		tk.Label(frame, text = title, font = ("Times New Roman", 14, "bold")).pack(pady = (0, 10))
		
		text_widget = tk.Text(frame, wrap = "word", font = ("Nimbus Roman", 10))
		scrollbar = tk.Scrollbar(frame, command = text_widget.yview)
		text_widget.configure(yscrollcommand = scrollbar.set)
		
		scrollbar.pack(side = "right", fill = "y")
		text_widget.pack(side = "left", fill = "both", expand = True)
		
		text_widget.insert("1.0", content)
		text_widget.config(state = "disabled")
		
		self._make_back_button(self.root)
		
	def _build_prompt_screen(self, title, fields, submit_callback):
		self._clear_screen()
		
		frame = tk.Frame(self.root)
		frame.place(relx = .5, rely = .4, anchor = "center")
		
		tk.Label(frame, text = title, font = ("Times New Roman", 14, "bold")).grid(row = 0, column = 0, columnspan = 2, pady = (0, 15))
		
		entries = {}
		for i, label_text in enumerate(fields, start = 1):
			tk.Label(frame, text = label_text, font = ("Times New Roman", 12)).grid(row = i, column = 0, sticky = "e", padx = 5, pady = 4)
			entry = tk.Entry(frame, font = ("Times New Roman", 12), width = 20)
			entry.grid(row = i, column = 1, pady = 4)
			entries[label_text] = entry
			
		tk.Button(frame, text = "Submit", font = ("Times New Roman", 10), width = 15, command = lambda: submit_callback(entries)).grid(row = len(fields) + 1, column = 0, columnspan = 2, pady = 15)
		
		self._make_back_button(self.root)
		return entries
		
		
	# Retrieve patient
	
	def _on_retrieve_patient(self):
		self.actions_performed.append("Retrieve patient")
		
		def submit(entries):
			pid = entries["Patient ID: "].get().strip()
			patient = Patient.retrieve_patient(pid, self.patients)
			
			if patient:
				self._show_scrollable_result(f"Patient {pid}", patient.to_display_string())
				
			else:
				messagebox.showwarning("Not found", f"No patient found with ID: {pid}")
		
		self._build_prompt_screen("Retrieve patient", ["Patient ID: "], submit)
		
	
	# Add patient
	
	def _on_add_patient(self):
		self._clear_screen()
		self.actions_performed.append("Add patient")
		
		# Scrollable form
		canvas = tk.Canvas(self.root)
		scrollbar = tk.Scrollbar(self.root, orient = "vertical", command = canvas.yview)
		form_frame = tk.Frame(canvas)
		
		form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion = canvas.bbox("all")))
		canvas.create_window((425, 0), window = form_frame, anchor = "n")
		canvas.configure(yscrollcommand = scrollbar.set)
		
		scrollbar.pack(side = "right", fill = "y")
		canvas.pack(side = "left", fill = "both", expand = True)
		
		# Title
		tk.Label(form_frame, text = "Add patient", font = ("Times New Roman", 14, "bold")).grid(row = 0, column = 0, columnspan = 2, pady = (10, 15))
		row = 1
		
		# Patient ID
		tk.Label(form_frame, text = "Patient ID: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_pid = tk.Entry(form_frame, font = ("Times New Roman", 10), width = 20)
		entry_pid.grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		# Age
		tk.Label(form_frame, text = "Age: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_age = tk.Entry(form_frame, font = ("Times New Roman", 10), width = 20)
		entry_age.grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		# Gender -> dropdown menu
		tk.Label(form_frame, text = "Gender: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		gender_var = tk.StringVar(value = "Female")
		ttk.Combobox(form_frame, textvariable = gender_var, values = Patient.GENDER_OPTIONS, state = "readonly", width = 18).grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		# BMI
		tk.Label(form_frame, text = "BMI: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_bmi = tk.Entry(form_frame, font = ("Times New Roman", 10), width = 20)
		entry_bmi.grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		# A1C
		tk.Label(form_frame, text = "A1C: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_a1c = tk.Entry(form_frame, font = ("Times New Roman", 10), width = 20)
		entry_a1c.grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		# BP Sys
		tk.Label(form_frame, text = "BP Sys: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_sys = tk.Entry(form_frame, font = ("Times New Roman", 10), width = 20)
		entry_sys.grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		# BP Dia
		tk.Label(form_frame, text = "BP Dia: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_dia = tk.Entry(form_frame, font = ("Times New Roman", 10), width = 20)
		entry_dia.grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		# Smoking -> dropdown menu
		tk.Label(form_frame, text = "Smoking: ", font = ("Times New Romans", 10)).grid(row = row, column = 0, sticky = "e", padx = 5, pady = 4)
		smoking_var = tk.StringVar(value = "No")
		ttk.Combobox(form_frame, textvariable = smoking_var, values = ["Yes", "No"], state = "readonly", width = 18).grid(row = row, column = 1, padx = 5, pady = 4)
		row += 1
		
		def submit():
			pid = entry_pid.get().strip()
			
			if not pid:
				messagebox.showwarning("Missing", "Patient ID is required.")
				return
			
			a1c_raw = entry_a1c.get().strip()
			a1c_val = a1c_raw if a1c_raw else None
			
			valid, msg = Patient.validate_patient_input(
				entry_age.get(),
				entry_bmi.get(),
				a1c_val,
				entry_sys.get(),
				entry_dia.get()
			)
			
			if not valid:
				messagebox.showerror("Validation error", msg)
				return
				
			new_patient = Patient(
				patient_id = pid,
				age = int(entry_age.get()),
				gender = gender_var.get(),
				bmi = float(entry_bmi.get()),
				a1c = float(a1c_raw) if a1c_raw else None,
				bp_sys = int(entry_sys.get()),
				bp_dia = int(entry_dia.get()),
				smoking = (smoking_var.get() == "Yes")
			)
			
			status, obj = Patient.add_patient(new_patient, self.patients)
			
			if status == "exists":
			# Patient already exists -> add a new encounter
				enc_date = datetime.now().strftime("%Y-%m-%d")
				self.hospital.add_encounter(
					pid,
					f"PR{random.randint(1, 20)}",
					f"D{random.randint(1, 4)}",
					enc_date,
					"Outpatient"
				)
				self.hospital.save_encounters()
				messagebox.showinfo(
					"Encounter added",
					f"Patient {pid} already exists. \nA new encounter on {enc_date} was created."
				)
			
			else:
				Patient.save_patients(self.patients)
				messagebox.showinfo("Success", f"Patient {pid} added successfully.")
				
			self._show_menu()
			
		tk.Button(form_frame, text = "Submit", font = ("Times New Roman", 10), width = 15, command = submit).grid(row = row, column = 0, columnspan = 2, pady = 15)
		
		# Back button
		btn_frame = tk.Frame(self.root)
		btn_frame.pack(side = "bottom", pady = 5)
		tk.Button(btn_frame, text = "<- Back to Menu", font = ("Times New Roman", 8), command = self._show_menu).pack()
		
	
	# Remove patient
	
	def _on_remove_patient(self):
		self.actions_performed.append("Remove patient")
		
		def submit(entries):
			pid = entries["Patient ID: "].get().strip()
			
			if Patient.remove_patient(pid, self.patients):
				self.hospital.remove_patient_records(pid)
				Patient.save_patients(self.patients)
				self.hospital.save_encounters()
				self.hospital.save_notes()
				self.hospital.save_procedures()
				messagebox.showinfo("Removed", f"All records for {pid} removed.")
				self._show_menu()
			
			else:
				messagebox.showwarning("Not found.", f"No patient found with ID:  {pid}")
		
		self._build_prompt_screen("Remove patient", ["Patient ID: "], submit)
		
		
	# Count visits
	
	def _on_count_visits(self):
		self._clear_screen()
		self.actions_performed.append("Count visits")
		
		frame = tk.Frame(self.root)
		frame.place(relx = .5, rely = .4, anchor = "center")
		
		tk.Label(frame, text = "Count visits", font = ("Times New Roman", 14, "bold")).grid(row = 0, column = 0, columnspan = 2, pady = (0, 15))
		
		tk.Label(frame, text = "Date (YYYY-MM-DD): ", font = ("Times New Roman", 12)).grid(row = 1, column = 0, sticky = "e", padx = 5)
		entry_date = tk.Entry(frame, font = ("Times New Roman", 12), width = 20)
		entry_date.grid(row = 1, column = 1, padx = 5)
		
		def submit():
			date_str = entry_date.get().strip()
			
			# Basic format check
			try:
				datetime.strptime(date_str, "%Y-%m-%d")
				
			except ValueError:
				messagebox.showerror("Invalid date.", "Please enter date as YYYY-MM-DD.")
				
				return
				
			total, per_patient, per_dept = self.hospital.count_visits(date_str)
			
			lines = [f"Date: {date_str}, Total visits: {total}\n"]
			
			if per_patient:
				lines.append("Visits pe patient: ")
				
				for pid, cnt in sorted(per_patient.items()):
					lines.append(f"{pid}: {cnt}")
					
			if per_dept:
				dept_map = {d["department_id"]: d["name"] for d in self.hospital.departments}
				lines.append("\nVisits per department: ")
				
				for did, cnt in sorted(per_dept.items()):
					name = dept_map.get(did, did)
					lines.append(f"{name}: {cnt}")
					
			self._show_scrollable_result("Visit count", "\n".join(lines))
			
		tk.Button(frame, text = "Count", font = ("Times New Roman", 10), width = 15, command = submit).grid(row = 2, column = 0, columnspan = 2, pady = 15)
		self._make_back_button(self.root)
	
	
	# View note
	
	def _on_view_note(self):
		self._clear_screen()
		self.actions_performed.append("View note")
		
		frame = tk.Frame(self.root)
		frame.place(relx = .5, rely = .4, anchor = "center")
		
		tk.Label(frame, text = "View clinical note", font = ("Times New Roman", 14, "bold")).grid(row = 0, column = 0, columnspan = 2, pady = (0, 15))
		
		tk.Label(frame, text = "Patient ID: ", font = ("Times New Roman", 12)).grid(row = 1, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_pid = tk.Entry(frame, font = ("Times New Roman", 12), width = 20)
		entry_pid.grid(row = 1, column = 1, padx = 5, pady = 4)
		
		tk.Label(frame, text = "Date (YYYY-MM-DD): ", font = ("Times New Roman", 12)).grid(row = 2, column = 0, sticky = "e", padx = 5, pady = 4)
		entry_date = tk.Entry(frame, font = ("Times New Roman", 12), width = 20)
		entry_date.grid(row =2, column = 1, padx = 5, pady = 4)
		
		def submit():
			pid = entry_pid.get().strip()
			date_str = entry_date.get().strip()
			
			notes = self.hospital.view_note(pid, date_str)
			
			if not notes:
				messagebox.showinfo("No notes.", f"No notes found for {pid} on {date_str}.")
				return
				
			lines = []
			
			for i, note in enumerate(notes, 1):
				lines.append(f"--- Note {i} ---")
				lines.append(f"Note ID: {note['note_id']}")
				lines.append(f"Type: {note['note_type']}")
				lines.append(f"Date: {note['note_date']}")
				lines.append(f"\n{note['note_text']}\n")
					
			self._show_scrollable_result(f"Notes for {pid} on {date_str}", "\n".join(lines))
			
		tk.Button(frame, text = "View", font = ("Times New Roman", 10), width = 15, command = submit).grid(row = 3, column = 0, columnspan = 2, pady = 15)
		self._make_back_button(self.root)
		
	
	# Generate key stats
	def _on_generate_stats(self):
		self.actions_performed.append("Generate key stats")
		report = self.hospital.generate_key_stats(self.patients)
		self._show_scrollable_result("Key stats", report)
		
		
	# Count encounters per patient (Admin)
	def _on_count_enc_per_patient(self):
		self.actions_performed.append("Count encounters per patient")
		counts = self.hospital.count_encounters_per_patient()
		
		lines = ["Encouners per patient (ranked): \n"]
		lines.append(f"{'Patient ID':<15}{'Encounters':>12}")
		lines.append("-" * 27)
		
		for pid, cnt in counts.items():
			lines.append(f"{pid:<15}{cnt:>12}")
		
		self._show_scrollable_result("Encounters per patient", "\n".join(lines))
		
	# Count encounters per department (Admin)
	def _on_count_enc_by_dept(self):
		self.actions_performed.append("Count encounters by department")
		counts = self.hospital.count_encounters_by_department()
		
		lines = ["Encouners by department: \n"]
		lines.append(f"{'Department':<20}{'Encounters':>12}")
		lines.append("-" * 32)
		
		for dept, cnt in counts.items():
			lines.append(f"{dept:<20}{cnt:>12}")
		
		self._show_scrollable_result("Encounters by department", "\n".join(lines))
		
	# Monitor provider workload (Admin)
	def _on_monitor_workload(self):
		self.actions_performed.append("Monitor provider workload")
		results = self.hospital.monitor_provider_workload()
		
		lines = ["Provider workload (ranked by encounters): \n"]
		lines.append(f"{'Provider':<15}{'Specialty':<22}{'Encounters':>10}")
		lines.append("-" * 47)
		
		for name, specialty, count in results:
			lines.append(f"{name:<15}{specialty:<22}{count:>10}")
		
		self._show_scrollable_result("Provider workload", "\n".join(lines))
	
	# Monitor department revenue (Management)
	def _on_monitor_revenue(self):
		self.actions_performed.append("Monitor department revenue")
		revenue = self.hospital.monitor_department_revenue()
		
		lines = ["Department revenue: \n"]
		lines.append(f"{'Department':<20}{'Total revenue':>15}")
		lines.append("-" * 35)
		
		for dept, total in revenue.items():
			lines.append(f"{dept:<20}${total:>13,.2f}")
		
		self._show_scrollable_result("Department revenue", "\n".join(lines))
		
		
	# Exit
	
	def _on_exit(self):
	# Log usage, save data, terminate
		
		if self.current_user:
			Hospital.log_usage(
				username = self.current_user.username,
				role = self.current_user.role,
				actions = self.actions_performed,
				login_time = self.login_time,
				success = True
			)
		
		# Save any pending patient changes
		Patient.save_patients(self.patients)
		self.hospital.save_encounters()
		self.hospital.save_notes()
		self.root.destroy()