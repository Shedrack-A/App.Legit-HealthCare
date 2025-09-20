from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from app.utils import is_password_strong
from app.models import PatientAccount

class PatientLoginForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login', render_kw={'class': 'btn btn-primary'})

class PatientSignUpForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    middle_name = StringField('Other/Middle Name')
    date_of_birth = StringField('Date of Birth') # String because it's read-only
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    department = StringField('Department') # Read-only
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account', render_kw={'class': 'btn btn-primary'})

    def validate_password(self, field):
        is_strong, message = is_password_strong(field.data)
        if not is_strong:
            raise ValidationError(message)

    def validate_staff_id(self, field):
        if PatientAccount.query.filter_by(staff_id=field.data).first():
            raise ValidationError('An account for this Staff ID already exists. Please proceed to login.')

    def validate_email(self, field):
        if PatientAccount.query.filter_by(email=field.data).first():
            raise ValidationError('This email address is already associated with an account.')

class PatientChangePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password', render_kw={'class': 'btn btn-primary'})

    def validate_password(self, field):
        is_strong, message = is_password_strong(field.data)
        if not is_strong:
            raise ValidationError(message)
