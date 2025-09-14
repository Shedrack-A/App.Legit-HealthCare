from flask import render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_required
from app import db
from app.admin import admin
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app.decorators import permission_required
from app.models import Role, Permission, User, TemporaryAccessCode, AuditLog, Patient, Setting
from .forms import RoleForm, EditUserForm, ChangePasswordForm, GenerateTempCodeForm, UploadForm, BrandingForm, EmailSettingsForm
import secrets
from datetime import datetime, timedelta, UTC
from app.utils import log_audit
from app.patient.routes import calculate_age

@admin.route('/')
@login_required
@permission_required('manage_roles') # Or a more generic 'access_admin_panel'
def index():
    return render_template('admin/index.html', title='Admin Dashboard')

@admin.route('/roles')
@login_required
@permission_required('manage_roles')
def list_roles():
    roles = Role.query.all()
    return render_template('admin/roles.html', title='Manage Roles', roles=roles)

@admin.route('/roles/new', methods=['GET', 'POST'])
@login_required
@permission_required('manage_roles')
def new_role():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data)
        for perm_id in form.permissions.data:
            perm = Permission.query.get(perm_id)
            role.permissions.append(perm)
        db.session.add(role)
        db.session.commit()
        log_audit('CREATE_ROLE', f'Role created: {role.name} (ID: {role.id})')
        flash('The role has been created.', 'success')
        return redirect(url_for('admin.list_roles'))
    return render_template('admin/role_form.html', form=form, title='New Role')

@admin.route('/roles/edit/<int:role_id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_roles')
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)

    if form.validate_on_submit():
        role.name = form.name.data
        # Clear existing permissions and add selected ones
        role.permissions = []
        for perm_id in form.permissions.data:
            perm = Permission.query.get(perm_id)
            role.permissions.append(perm)
        db.session.commit()
        log_audit('EDIT_ROLE', f'Role edited: {role.name} (ID: {role.id})')
        flash('The role has been updated.', 'success')
        return redirect(url_for('admin.list_roles'))

    # Pre-select the permissions for the role
    form.permissions.data = [p.id for p in role.permissions]
    return render_template('admin/role_form.html', form=form, title='Edit Role', role=role)

@admin.route('/roles/delete/<int:role_id>', methods=['POST'])
@login_required
@permission_required('manage_roles')
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    if role.name in ['Admin', 'New User']:
        flash('You cannot delete this protected role.', 'danger')
        return redirect(url_for('admin.list_roles'))
    log_audit('DELETE_ROLE', f'Role deleted: {role.name} (ID: {role.id})')
    db.session.delete(role)
    db.session.commit()
    flash('The role has been deleted.', 'success')
    return redirect(url_for('admin.list_roles'))

@admin.route('/users')
@login_required
@permission_required('manage_users')
def list_users():
    users = User.query.paginate(per_page=20)
    return render_template('admin/users.html', title='Manage Users', users=users)

@admin.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_users')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        # Clear existing roles and add selected ones
        user.roles = []
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            user.roles.append(role)

        db.session.commit()
        log_audit('EDIT_USER', f'User edited: {user.phone_number} (ID: {user.id})')
        flash('The user has been updated.', 'success')
        return redirect(url_for('admin.list_users'))

    form.roles.data = [role.id for role in user.roles]
    return render_template('admin/edit_user.html', form=form, title='Edit User', user=user)

@admin.route('/users/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_users')
def change_user_password(user_id):
    user = User.query.get_or_404(user_id)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        log_audit('ADMIN_CHANGE_PASSWORD', f'Password changed for user: {user.phone_number} (ID: {user.id})')
        flash(f'Password for {user.first_name} {user.last_name} has been updated.', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/change_password.html', form=form, title='Change Password', user=user)

@admin.route('/temp_codes', methods=['GET', 'POST'])
@login_required
@permission_required('manage_temp_codes')
def manage_temp_codes():
    form = GenerateTempCodeForm()
    if form.validate_on_submit():
        expiry = datetime.now(UTC) + timedelta(minutes=form.duration.data)
        code_str = f"LHCSL-{secrets.token_hex(4).upper()}{secrets.token_hex(4).upper()}"

        new_code = TemporaryAccessCode(
            code=code_str,
            user_id=form.user.data,
            permission_id=form.permission.data,
            expiry_time=expiry,
            is_single_use=form.is_single_use.data
        )
        db.session.add(new_code)
        db.session.commit()
        log_audit('GENERATE_TEMP_CODE', f'Temp code generated for user ID {new_code.user_id} with permission ID {new_code.permission_id}')
        flash(f'New temporary access code generated: {code_str}', 'success')
        return redirect(url_for('admin.manage_temp_codes'))

    codes = TemporaryAccessCode.query.order_by(TemporaryAccessCode.id.desc()).all()
    return render_template('admin/temp_codes.html', title='Temporary Access Codes', form=form, codes=codes, now=datetime.utcnow)

@admin.route('/temp_codes/revoke/<int:code_id>', methods=['POST'])
@login_required
@permission_required('manage_temp_codes')
def revoke_temp_code(code_id):
    code = TemporaryAccessCode.query.get_or_404(code_id)
    code.is_active = False
    db.session.commit()
    log_audit('REVOKE_TEMP_CODE', f'Temp code revoked: {code.code} (ID: {code.id})')
    flash(f'Code {code.code} has been revoked.', 'success')
    return redirect(url_for('admin.manage_temp_codes'))

@admin.route('/upload_data', methods=['GET', 'POST'])
@login_required
@permission_required('upload_data')
def upload_data():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.excel_file.data
        filename = secure_filename(f.filename)
        filepath = os.path.join('uploads', filename)
        f.save(filepath)

        try:
            df = pd.read_excel(filepath)

            required_columns = ['staff_id', 'patient_id', 'first_name', 'last_name', 'department', 'gender', 'date_of_birth', 'contact_phone', 'email_address', 'race', 'nationality']
            if not all(col in df.columns for col in required_columns):
                flash('Excel file is missing one or more required columns.', 'danger')
                return redirect(url_for('admin.upload_data'))

            success_count = 0
            error_rows = []

            for index, row in df.iterrows():
                # Basic validation
                if pd.isna(row['staff_id']) or pd.isna(row['first_name']) or pd.isna(row['date_of_birth']):
                    error_rows.append(index + 2) # +2 to account for 0-based index and header
                    continue

                # Check for duplicates before adding
                exists = Patient.query.filter_by(
                    staff_id=str(row['staff_id']),
                    company=session.get('company', 'DCP'),
                    screening_year=session.get('year', datetime.now(UTC).year)
                ).first()

                if exists:
                    error_rows.append(index + 2)
                    continue

                age = calculate_age(row['date_of_birth'].to_pydatetime().date())

                patient = Patient(
                    staff_id=str(row['staff_id']),
                    patient_id=str(row['patient_id']),
                    first_name=row['first_name'],
                    middle_name=row.get('middle_name', ''),
                    last_name=row['last_name'],
                    department=row['department'],
                    gender=row['gender'],
                    date_of_birth=row['date_of_birth'],
                    age=age,
                    contact_phone=str(row['contact_phone']),
                    email_address=row['email_address'],
                    race=row['race'],
                    nationality=row['nationality'],
                    company=session.get('company', 'DCP'),
                    screening_year=session.get('year', datetime.now(UTC).year)
                )
                db.session.add(patient)
                success_count += 1

            db.session.commit()
            log_audit('UPLOAD_PATIENTS', f'Successfully uploaded {success_count} patients from file: {filename}')
            flash(f'Successfully imported {success_count} patient records.', 'success')
            if error_rows:
                flash(f'Skipped {len(error_rows)} rows due to missing data or duplicates: {", ".join(map(str, error_rows))}', 'warning')

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during processing: {e}', 'danger')
        finally:
            os.remove(filepath) # Clean up the uploaded file

        return redirect(url_for('admin.upload_data'))

    return render_template('admin/upload_data.html', title='Upload Patient Data', form=form, session=session)

@admin.route('/audit_trails')
@login_required
@permission_required('view_audit_log')
def audit_trails():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=50)
    return render_template('admin/audit_trails.html', title='Audit Trails', logs=logs)

@admin.route('/api/notifications')
@login_required
@permission_required('manage_roles') # Only admins should see notifications
def get_notifications():
    notifiable_actions = ['GENERATE_TEMP_CODE', 'REVOKE_TEMP_CODE', 'USER_REGISTER']
    notifications = AuditLog.query.filter(
        AuditLog.action.in_(notifiable_actions),
        AuditLog.notified == False
    ).order_by(AuditLog.timestamp.desc()).limit(5).all()

    return jsonify([{
        'id': n.id,
        'action': n.action,
        'details': n.details,
        'timestamp': n.timestamp.isoformat() + 'Z'
    } for n in notifications])

@admin.route('/api/notifications/mark_read', methods=['POST'])
@login_required
@permission_required('manage_roles')
def mark_notifications_read():
    ids_to_mark = request.json.get('ids', [])
    if ids_to_mark:
        AuditLog.query.filter(AuditLog.id.in_(ids_to_mark)).update({'notified': True}, synchronize_session=False)
        db.session.commit()
    return jsonify({'status': 'success'})

@admin.route('/branding', methods=['GET', 'POST'])
@login_required
@permission_required('manage_settings')
def branding():
    form = BrandingForm()
    if form.validate_on_submit():
        if form.light_logo.data:
            f = form.light_logo.data
            filename = secure_filename('light_logo' + os.path.splitext(f.filename)[1])
            filepath = os.path.join('app/static/logos', filename)
            f.save(filepath)

            setting = Setting.query.filter_by(key='light_logo_url').first()
            if not setting:
                setting = Setting(key='light_logo_url')
            setting.value = f'/static/logos/{filename}'
            db.session.add(setting)

        if form.dark_logo.data:
            f = form.dark_logo.data
            filename = secure_filename('dark_logo' + os.path.splitext(f.filename)[1])
            filepath = os.path.join('app/static/logos', filename)
            f.save(filepath)

            setting = Setting.query.filter_by(key='dark_logo_url').first()
            if not setting:
                setting = Setting(key='dark_logo_url')
            setting.value = f'/static/logos/{filename}'
            db.session.add(setting)

        db.session.commit()
        log_audit('UPDATE_BRANDING', 'Updated site logos.')
        flash('Branding has been updated.', 'success')
        return redirect(url_for('admin.branding'))

    logos = {
        'light': Setting.query.filter_by(key='light_logo_url').first(),
        'dark': Setting.query.filter_by(key='dark_logo_url').first()
    }
    return render_template('admin/branding.html', title='Branding', form=form, logos=logos)

@admin.route('/email_settings', methods=['GET', 'POST'])
@login_required
@permission_required('manage_settings')
def email_settings():
    form = EmailSettingsForm()
    if form.validate_on_submit():
        # Update or create MAIL_USERNAME
        username_setting = Setting.query.filter_by(key='MAIL_USERNAME').first()
        if not username_setting:
            username_setting = Setting(key='MAIL_USERNAME')
        username_setting.value = form.mail_username.data
        db.session.add(username_setting)

        # Update or create MAIL_PASSWORD, only if a new password is provided
        if form.mail_password.data:
            password_setting = Setting.query.filter_by(key='MAIL_PASSWORD').first()
            if not password_setting:
                password_setting = Setting(key='MAIL_PASSWORD')
            password_setting.value = form.mail_password.data
            db.session.add(password_setting)

        db.session.commit()
        log_audit('UPDATE_EMAIL_SETTINGS', 'Updated email configuration.')
        flash('Email settings have been updated. The application may need to be restarted for changes to take effect.', 'success')
        return redirect(url_for('admin.email_settings'))

    # Pre-populate the form
    username = Setting.query.filter_by(key='MAIL_USERNAME').first()
    if username:
        form.mail_username.data = username.value

    return render_template('admin/email_settings.html', title='Email Settings', form=form)
