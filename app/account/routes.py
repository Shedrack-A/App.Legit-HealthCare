from flask import render_template, redirect, url_for, flash, session, request
from markupsafe import Markup
from flask_login import login_required, current_user, login_user
from app import db, bcrypt
from app.account import account
from .forms import ChangePasswordForm, Enable2FAForm, Disable2FAForm, Verify2FAForm, RecoveryCodeForm, ChangePersonalInfoForm
from app.models import User, UserRecoveryCode
from app.utils import is_password_strong, log_audit
import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
import secrets

def generate_recovery_codes(user):
    """Generate and store new recovery codes for a user."""
    # Delete old codes
    UserRecoveryCode.query.filter_by(user_id=user.id).delete()

    recovery_codes = []
    for _ in range(10):
        code = secrets.token_hex(6)
        recovery_codes.append(code)

        # Store hashed version
        code_hash_str = bcrypt.generate_password_hash(code).decode('utf-8')
        new_code = UserRecoveryCode(user_id=user.id, code_hash=code_hash_str)
        db.session.add(new_code)

    db.session.commit()
    return recovery_codes

@account.route('/settings')
@login_required
def settings():
    return render_template('account/settings.html', title='Account Settings')

from wtforms.validators import DataRequired, Length
@account.route('/change_personal_info', methods=['GET', 'POST'])
@login_required
def change_personal_info():
    form = ChangePersonalInfoForm(obj=current_user)

    if current_user.otp_enabled:
        form.token.validators = [DataRequired(), Length(min=6, max=6)]
    else:
        form.password.validators = [DataRequired()]

    if form.validate_on_submit():
        auth_ok = False
        if current_user.otp_enabled:
            totp = pyotp.TOTP(current_user.otp_secret)
            if totp.verify(form.token.data):
                auth_ok = True
            else:
                flash('Invalid 2FA token.', 'danger')
        else:
            if current_user.verify_password(form.password.data):
                auth_ok = True
            else:
                flash('Incorrect password.', 'danger')

        if auth_ok:
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email_address = form.email.data
            current_user.phone_number = form.phone_number.data
            db.session.commit()
            log_audit('USER_UPDATE_INFO', f'User {current_user.id} updated their personal information.')
            flash('Your personal information has been updated.', 'success')
            return redirect(url_for('account.settings'))

    return render_template('account/change_personal_info.html', title='Change Personal Information', form=form)

@account.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.current_password.data):
            is_strong, message = is_password_strong(form.new_password.data)
            if is_strong:
                current_user.password = form.new_password.data
                db.session.commit()
                log_audit('USER_CHANGE_PASSWORD', f'User {current_user.id} changed their own password.')
                flash('Your password has been updated.', 'success')
                return redirect(url_for('account.settings'))
            else:
                flash(message, 'danger')
        else:
            flash('Incorrect current password.', 'danger')
    return render_template('account/change_password.html', title='Change Password', form=form)

@account.route('/2fa', methods=['GET', 'POST'])
@login_required
def two_factor_auth():
    enable_form = Enable2FAForm()
    disable_form = Disable2FAForm()
    qr_code_svg = None

    if not current_user.otp_enabled:
        if 'otp_secret_in_session' not in session:
            session['otp_secret_in_session'] = pyotp.random_base32()

        totp = pyotp.TOTP(session['otp_secret_in_session'])
        provisioning_uri = totp.provisioning_uri(name=current_user.email_address, issuer_name="Legit HealthCare")

        img = qrcode.make(provisioning_uri, image_factory=qrcode.image.svg.SvgPathImage)
        stream = BytesIO()
        img.save(stream)
        qr_code_svg = Markup(stream.getvalue().decode())
        stream.close()

    return render_template('account/two_factor_auth.html', title='2FA Authentication',
                           enable_form=enable_form, disable_form=disable_form, qr_code_svg=qr_code_svg)

@account.route('/enable_2fa', methods=['POST'])
@login_required
def enable_2fa():
    form = Enable2FAForm()
    if form.validate_on_submit() and 'otp_secret_in_session' in session:
        totp = pyotp.TOTP(session['otp_secret_in_session'])
        if totp.verify(form.token.data):
            current_user.otp_secret = session.pop('otp_secret_in_session')
            current_user.otp_enabled = True
            db.session.commit()

            # Generate and show recovery codes
            recovery_codes = generate_recovery_codes(current_user)
            flash('2FA has been enabled successfully! Please save your recovery codes.', 'success')
            log_audit('USER_ENABLE_2FA', f'User {current_user.id} enabled 2FA.')
            return render_template('account/recovery_codes.html', title='Your Recovery Codes', recovery_codes=recovery_codes)
        else:
            flash('Invalid authenticator code.', 'danger')
    return redirect(url_for('account.two_factor_auth'))

@account.route('/disable_2fa', methods=['POST'])
@login_required
def disable_2fa():
    form = Disable2FAForm()
    if form.validate_on_submit():
        current_user.otp_enabled = False
        current_user.otp_secret = None
        UserRecoveryCode.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        log_audit('USER_DISABLE_2FA', f'User {current_user.id} disabled 2FA.')
        flash('2FA has been disabled.', 'success')
    return redirect(url_for('account.two_factor_auth'))

@account.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'user_id_for_2fa' not in session:
        return redirect(url_for('auth.login'))

    form = Verify2FAForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id_for_2fa'])
        if user:
            totp = pyotp.TOTP(user.otp_secret)
            if totp.verify(form.token.data):
                session.pop('user_id_for_2fa')
                login_user(user)
                log_audit('USER_LOGIN_2FA', f'User {user.id} completed 2FA login.')
                flash('Logged in successfully.', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid authenticator code.', 'danger')
        else:
            flash('User not found.', 'danger')
            session.pop('user_id_for_2fa')
            return redirect(url_for('auth.login'))

    return render_template('account/verify_2fa.html', title='Verify 2FA', form=form)

@account.route('/verify_recovery', methods=['GET', 'POST'])
def verify_recovery():
    if 'user_id_for_2fa' not in session:
        return redirect(url_for('auth.login'))

    form = RecoveryCodeForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id_for_2fa'])
        submitted_code = form.recovery_code.data

        if not user:
            flash('User not found.', 'danger')
            session.pop('user_id_for_2fa')
            return redirect(url_for('auth.login'))

        # Find a matching, unused code
        for code_record in user.recovery_codes.filter_by(used=False):
            if bcrypt.check_password_hash(code_record.code_hash, submitted_code):
                code_record.used = True
                db.session.commit()

                session.pop('user_id_for_2fa')
                login_user(user)

                log_audit('USER_LOGIN_RECOVERY', f'User {user.id} logged in with a recovery code.')
                flash('Successfully logged in with recovery code.', 'success')
                return redirect(url_for('main.dashboard'))

        flash('Invalid or already used recovery code.', 'danger')

    return render_template('account/verify_recovery_code.html', title='Use Recovery Code', form=form)
