from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class ChangePasswordForm(FlaskForm):
    """Form for users to change their own password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=10)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit_password = SubmitField('Change Password')

class Enable2FAForm(FlaskForm):
    """Form to verify TOTP token to enable 2FA."""
    token = StringField('Authenticator Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit_enable = SubmitField('Enable 2FA')

class Verify2FAForm(FlaskForm):
    """Form to enter 2FA token during login."""
    token = StringField('Authenticator Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit_verify = SubmitField('Verify')

class Disable2FAForm(FlaskForm):
    """Form to disable 2FA."""
    submit_disable = SubmitField('Disable 2FA')

class RecoveryCodeForm(FlaskForm):
    """Form to enter a 2FA recovery code."""
    recovery_code = StringField('Recovery Code', validators=[DataRequired()])
    submit_recovery = SubmitField('Use Recovery Code')
