from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from app.models import Permission, Role

class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired()])
    permissions = SelectMultipleField('Permissions', coerce=int)
    submit = SubmitField('Save Role')

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.order_by('name')]

class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    roles = SelectMultipleField('Roles', coerce=int)
    submit = SubmitField('Update User')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(r.id, r.name) for r in Role.query.order_by('name')]

class ChangePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')
