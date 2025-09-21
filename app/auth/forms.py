from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length, Optional, Email
from app.models import User
from app.utils import is_password_strong

import re

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    phone_number = StringField('Phone Number', validators=[DataRequired()], render_kw={"placeholder": "+234..."})
    email_address = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up', render_kw={'class': 'btn btn-primary'})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email_address(self, email_address):
        user = User.query.filter_by(email_address=email_address.data).first()
        if user:
            raise ValidationError('That email address is already registered. Please choose a different one.')

    def validate_password(self, field):
        is_strong, message = is_password_strong(field.data)
        if not is_strong:
            raise ValidationError(message)

    def validate_phone_number(self, phone_number):
        # Check format
        if not re.match(r'^\+234\d{10}$', phone_number.data):
            raise ValidationError('Phone number must be in the format +234 followed by 10 digits (e.g., +2348012345678).')

        # Check for uniqueness
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('That phone number is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    login = StringField('Username or Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login', render_kw={'class': 'btn btn-primary'})

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset', render_kw={'class': 'btn btn-primary'})

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password', render_kw={'class': 'btn btn-primary'})

    def validate_password(self, field):
        is_strong, message = is_password_strong(field.data)
        if not is_strong:
            raise ValidationError(message)
