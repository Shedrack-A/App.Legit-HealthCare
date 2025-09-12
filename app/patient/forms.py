from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

# The user provided this list of departments.
DEPARTMENTS = sorted([
    "Admin", "Ham-Admin", "Security", "Packing Plant", "Power Plant", "Mechanical",
    "Kiln", "Kiln Mechanical", "Instrumentation", "Mines", "Crusher", "Special Duties",
    "A.G.O", "Assets", "C.N.G", "Cement Mill", "Central Maintenance", "Civil",
    "Civil Engineering", "Compliance", "D.H.U", "Electrical", "Help Desk", "HSE",
    "I.T", "Inbound", "LMV", "Loading Crew", "Logistics", "Mechanical Rawmills",
    "Medical", "Methods", "Mix-Storage", "National Patrol", "Operations", "Process",
    "Procurement", "Production", "Projectt", "Purchase", "Quality Assurance",
    "Raw Mill", "Safety", "Stores", "Traffic", "Tyre Re-Trading", "Workshop",
    "Workshop & Utility"
])

# Placeholder lists for race and nationality
RACES = ["Asian", "African", "Caucasian", "Hispanic", "Other"]
NATIONALITIES = ["Nigerian", "Ghanian", "American", "British", "Other"] # Placeholder

class PatientRegistrationForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    patient_id = StringField('Patient ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    department = SelectField('Department', choices=[(d, d) for d in DEPARTMENTS], validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    contact_phone = StringField('Contact Phone', validators=[DataRequired()])
    email_address = StringField('Email Address', validators=[Optional()])
    race = SelectField('Race/Continent', choices=[(r, r) for r in RACES], validators=[DataRequired()])
    nationality = SelectField('Nationality', choices=[(n, n) for n in NATIONALITIES], validators=[DataRequired()])
    submit = SubmitField('Register Patient')
