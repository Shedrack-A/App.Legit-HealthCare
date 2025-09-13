from app import create_app, db, socketio
import os
from app.models import User, Role, Permission
import click

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role}

@app.cli.command("create-admin")
def create_admin():
    """Creates the admin user."""
    admin_role = Role.query.filter_by(name='Admin').first()
    if admin_role is None:
        admin_role = Role(name='Admin')
        db.session.add(admin_role)

    admin_user = User.query.filter_by(phone_number='admin').first()
    if admin_user is None:
        admin_user = User(
            first_name='Admin',
            last_name='User',
            phone_number='admin',
            password='adminpass'
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully.')
    else:
        print('Admin user already exists.')

@app.cli.command("init-permissions")
def init_permissions():
    """Initializes the database with all application permissions."""
    permissions = [
        'manage_users',
        'manage_roles',
        'manage_permissions',
        'view_sensitive_data',
        'edit_patient',
        'delete_patient',
        'enter_consultation',
        'enter_lab_results',
        'manage_temp_codes',
        'view_audit_log',
        'upload_data',
        'manage_settings'
    ]

    for perm_name in permissions:
        perm = Permission.query.filter_by(name=perm_name).first()
        if not perm:
            perm = Permission(name=perm_name)
            db.session.add(perm)

    # Assign all permissions to the Admin role
    admin_role = Role.query.filter_by(name='Admin').first()
    if admin_role:
        all_perms = Permission.query.all()
        admin_role.permissions = all_perms

    db.session.commit()
    print('Permissions have been initialized and assigned to Admin role.')

if __name__ == '__main__':
    socketio.run(app, debug=True)
