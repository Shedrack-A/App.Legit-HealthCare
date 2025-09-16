from flask import render_template, redirect, url_for, flash, session, request, Markup
from flask_login import login_required, current_user, login_user
from app import db, bcrypt
from app.account import account
from .forms import ChangePasswordForm, Enable2FAForm, Disable2FAForm, Verify2FAForm
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

@account.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    password_form = ChangePasswordForm()
    enable_2fa_form = Enable2FAForm()
    disable_2fa_form = Disable2FAForm()

    qr_code_svg = None
    if not current_user.otp_enabled and 'otp_secret_in_session' not in session:
        # Generate a new secret for the user to scan
        session['otp_secret_in_session'] = pyotp.random_base32()

    if 'otp_secret_in_session' in session:
        # Generate QR code
        totp = pyotp.TOTP(session['otp_secret_in_session'])
        provisioning_uri = totp.provisioning_uri(name=current_user.email_address or current_user.phone_number, issuer_name="Legit HealthCare")

        img = qrcode.make(provisioning_uri, image_factory=qrcode.image.svg.SvgPathImage)
        stream = BytesIO()
        img.save(stream)
        qr_code_svg = Markup(stream.getvalue().decode())
        stream.close()

    if password_form.submit_password.data and password_form.validate_on_submit():
        if current_user.verify_password(password_form.current_password.data):
            is_strong, message = is_password_strong(password_form.new_password.data)
            if is_strong:
                current_user.password = password_form.new_password.data
                db.session.commit()
                log_audit('USER_CHANGE_PASSWORD', f'User {current_user.id} changed their own password.')
                flash('Your password has been updated.', 'success')
            else:
                flash(message, 'danger')
        else:
            flash('Incorrect current password.', 'danger')
        return redirect(url_for('account.settings'))

    return render_template('account/settings.html', title='Account Settings',
                           password_form=password_form,
                           enable_2fa_form=enable_2fa_form,
                           disable_2fa_form=disable_2fa_form,
                           qr_code_svg=qr_code_svg)

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
    return redirect(url_for('account.settings'))

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
    return redirect(url_for('account.settings'))

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
                # Handle recovery code logic here if needed
                flash('Invalid authenticator code.', 'danger')
        else:
            flash('User not found.', 'danger')
            session.pop('user_id_for_2fa')
            return redirect(url_for('auth.login'))

    return render_template('account/verify_2fa.html', title='Verify 2FA', form=form)
