from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email, Optional

class ChangePersonalInfoForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Confirm with Password', validators=[Optional()])
    token = StringField('2FA Authenticator Code', validators=[Optional(), Length(min=6, max=6)])
    submit = SubmitField('Save Changes', render_kw={'class': 'btn btn-primary'})

class ChangePasswordForm(FlaskForm):
    """Form for users to change their own password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=10)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit_password = SubmitField('Change Password', render_kw={'class': 'btn btn-primary'})

class Enable2FAForm(FlaskForm):
    """Form to verify TOTP token to enable 2FA."""
    token = StringField('Authenticator Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit_enable = SubmitField('Enable 2FA', render_kw={'class': 'btn btn-primary'})

class Verify2FAForm(FlaskForm):
    """Form to enter 2FA token during login."""
    token = StringField('Authenticator Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit_verify = SubmitField('Verify', render_kw={'class': 'btn btn-primary'})

class Disable2FAForm(FlaskForm):
    """Form to disable 2FA."""
    submit_disable = SubmitField('Disable 2FA', render_kw={'class': 'btn btn-danger'})

class RecoveryCodeForm(FlaskForm):
    """Form to enter a 2FA recovery code."""
    recovery_code = StringField('Recovery Code', validators=[DataRequired()])
    submit_recovery = SubmitField('Use Recovery Code', render_kw={'class': 'btn btn-secondary'})
