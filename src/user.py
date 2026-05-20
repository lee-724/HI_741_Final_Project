import csv
import os

class User:
# Represents an authenticated user with role-based access control

	ROLE_ACTIONS = {
		"clinician": [
			"Retrieve patient",
			"Add patient",
			"Remove patient",
			"Count visits",
			"View note",
			"Generate key stats",
			"Exit"
		],
		"nurse": [
			"Retrieve patient",
			"Add patient",
			"Remove patient",
			"Count visits",
			"View note",
			"Generate key stats",
			"Exit"
		],
		"admin": [
			"Count encounters per patient",
			"Count encounters by department",
			"Monitor provider workload",
			"Exit"
		],
		"management": [
			"Monitor department revenue",
			"Generate key stats",
			"Exit"
		]
	}
	
	PHI_ROLES = {"clinician", "nurse"}
	
	def __init__(self, username, password, role):
	# Initialize a user instance
		self.username = username
		self.password = password
		self.role = role # admin, clinician, nurse, management
		
	def __repr__(self):
		return f"User (username = '{self.username}', role = {self.role}')"


	# --- Loading credentials from CSV ---

	@staticmethod		
	def load_credentials(filepath = "./data/credentials.csv"):
	# Read credentials.csv and return a list of User object
		users = []
		if not os.path.exists(filepath):
			print(f"[Warning] Credential file not found: {filepath}")
			return users
		
		with open(filepath, "r", newline = "") as f:
			reader = csv.DictReader(f)
			for row in reader:
				users.append(
					User(
						username = row["username"].strip(),
						password = row["password"].strip(),
						role = row["role"].strip()
					)
				)
		return users

	@staticmethod		
	def authenticate(username, password, users):
	# Match username and password against the loaded user list
		for user in users:
			if user.username == username and user.password == password:
				return user
		return None


	# --- Role-based access ---
		
	def get_allowed_actions(self):
	# Return a list of action strings permitted for this user's role
		return self.ROLE_ACTIONS.get(self.role, [])
		
	def can_access_phi(self):
	# Check whether the user's role permits access to PHI
		return self.role in self.PHI_ROLES

	def is_clinical_role(self):
	# Check if the user has a clinical role (clinician/nurse)
		return self.role in ("clinician", "nurse")
		
	def is_admin(self):
	# Check if the user has the admin role
		return self.role == "admin"
		
	def is_management(self):
	# Check if the user has the management role
		return self.role == "management"