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
    """Creates the default admin user."""
    # Ensure the Admin role exists and has all permissions
    init_permissions()

    admin_role = Role.query.filter_by(name='Admin').first()
    admin_user = User.query.filter_by(username='admin').first()

    if admin_user is None:
        admin_user = User(
            username='admin',
            email_address='admin@local.host',
            first_name='Admin',
            last_name='User',
            phone_number='+2340000000000', # Placeholder phone
            password='adminpass'
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully. Credentials: admin / adminpass')
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
        'manage_settings',
        'access_director_page',
        'generate_patient_report'
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
