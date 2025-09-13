from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.admin import admin
from flask import render_template, redirect, url_for, flash, request
from app.decorators import permission_required
from app.models import Role, Permission, User, TemporaryAccessCode, AuditLog
from .forms import RoleForm, EditUserForm, ChangePasswordForm, GenerateTempCodeForm
import secrets
from datetime import datetime, timedelta, UTC
from app.utils import log_audit

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

@admin.route('/audit_trails')
@login_required
@permission_required('view_audit_log')
def audit_trails():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=50)
    return render_template('admin/audit_trails.html', title='Audit Trails', logs=logs)
