from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth
from app.models import User, Role
from app.auth.forms import LoginForm, RegistrationForm
from app.utils import log_audit

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
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
        log_audit('USER_REGISTER', f'New user registered: {user.phone_number} (ID: {user.id})')
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone_number=form.phone_number.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            log_audit('USER_LOGIN', f'User logged in: {user.phone_number}')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid phone number or password.', 'danger')
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
@login_required
def logout():
    log_audit('USER_LOGOUT', f'User logged out: {current_user.phone_number}')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
