from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectMultipleField, PasswordField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Optional, Email
from app.models import Permission, Role, User

class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired()])
    permissions = SelectMultipleField('Permissions', coerce=int, render_kw={'class': 'select2-enable'})
    submit = SubmitField('Save Role')

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.order_by('name')]

class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    roles = SelectMultipleField('Roles', coerce=int, render_kw={'class': 'select2-enable'})
    submit = SubmitField('Update User')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(r.id, r.name) for r in Role.query.order_by('name')]

class ChangePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')

class GenerateTempCodeForm(FlaskForm):
    user = SelectField('User', coerce=int, validators=[DataRequired()], render_kw={'class': 'select2-enable'})
    permission = SelectField('Permission', coerce=int, validators=[DataRequired()], render_kw={'class': 'select2-enable'})
    duration = IntegerField('Duration (minutes)', default=60, validators=[DataRequired(), NumberRange(min=1)])
    is_single_use = BooleanField('Single Use Only', default=True)
    submit = SubmitField('Generate Code')

    def __init__(self, *args, **kwargs):
        super(GenerateTempCodeForm, self).__init__(*args, **kwargs)
        self.user.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.phone_number})") for u in User.query.order_by('last_name')]
        self.permission.choices = [(p.id, p.name) for p in Permission.query.order_by('name')]

class UploadForm(FlaskForm):
    excel_file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx'], 'Excel files only!')
    ])
    submit = SubmitField('Upload and Process')

class BrandingForm(FlaskForm):
    hospital_name = StringField('Hospital Name', validators=[Optional()])
    organization_name = StringField('Organization Name', validators=[Optional()])
    light_logo = FileField('Light Theme Logo', validators=[FileAllowed(['jpg', 'png', 'svg'], 'Images only!')])
    dark_logo = FileField('Dark Theme Logo', validators=[FileAllowed(['jpg', 'png', 'svg'], 'Images only!')])
    favicon = FileField('Favicon', validators=[FileAllowed(['ico', 'png'], 'ICO or PNG files only!')])
    submit = SubmitField('Save Settings')

class EmailSettingsForm(FlaskForm):
    mail_username = StringField('Sender Email (Gmail Address)', validators=[Optional(), Email()])
    mail_password = PasswordField('Gmail App Password', validators=[Optional()])
    mail_sender_name = StringField('Sender Name (e.g., Legit HealthCare)', validators=[Optional()])
    submit = SubmitField('Save Email Settings')
