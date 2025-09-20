from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from flask_login import current_user
from app.auth import auth
from app.models import User, Role
from app.auth.forms import LoginForm, RegistrationForm
from app.utils import log_audit, send_email

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            phone_number=form.phone_number.data,
            email_address=form.email_address.data,
            password=form.password.data
        )
        db.session.add(user)
        # Assign a default role
        new_user_role = Role.query.filter_by(name='New User').first()
        if new_user_role is None:
            # Create the 'New User' role if it doesn't exist
            new_user_role = Role(name='New User')
            db.session.add(new_user_role)
        user.roles.append(new_user_role)
        db.session.commit()
        # The user object has the new ID after the commit
        if user.email_address:
            send_email(user.email_address, 'Welcome to Legit HealthCare Services', 'email/welcome', user=user)
        log_audit('USER_REGISTER', f'New user registered: {user.username} (ID: {user.id})')
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            # Check if 2FA is enabled
            if user.otp_enabled:
                session['user_id_for_2fa'] = user.id
                return redirect(url_for('account.verify_2fa'))

            # If 2FA is not enabled, log in directly
            login_user(user, remember=form.remember.data)
            log_audit('USER_LOGIN', f'User logged in: {user.username}')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
@login_required
def logout():
    log_audit('USER_LOGOUT', f'User logged out: {current_user.username}')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

from .forms import ForgotPasswordForm, ResetPasswordForm
from app.models import PasswordResetToken, PatientAccount
import secrets
from datetime import datetime, timedelta, UTC

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email.data).first()
        patient = PatientAccount.query.filter_by(email=form.email.data).first()

        if user or patient:
            token = secrets.token_urlsafe(20)
            expiry_time = datetime.now(UTC) + timedelta(hours=1)

            new_token = PasswordResetToken(
                token=token,
                expiry_time=expiry_time
            )
            if user:
                new_token.user_id = user.id
            if patient:
                new_token.patient_account_id = patient.id

            db.session.add(new_token)
            db.session.commit()

            # Create a generic user object for the email template
            email_user = user if user else patient
            email_user.first_name = user.first_name if user else "Patient"

            # Send email
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email(
                recipient=form.email.data,
                subject='Password Reset Request',
                template='email/password_reset',
                user=email_user,
                reset_url=reset_url
            )

            flash('A password reset link has been sent to your email.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Email address not found.', 'danger')

    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_entry = PasswordResetToken.query.filter_by(token=token).first()

    if not token_entry or token_entry.used or token_entry.expiry_time < datetime.now(UTC):
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if token_entry.user_id:
            user = User.query.get(token_entry.user_id)
            user.password = form.password.data
        elif token_entry.patient_account_id:
            patient = PatientAccount.query.get(token_entry.patient_account_id)
            patient.password = form.password.data

        token_entry.used = True
        db.session.commit()

        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Reset Password', form=form)
