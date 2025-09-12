from app.models import User, Role, Permission, TemporaryAccessCode
from app import db
from datetime import datetime, timedelta

def test_registration_and_login(client):
    # Test registration
    response = client.post('/auth/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'phone_number': '1112223333',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Congratulations, you are now a registered user!' in response.data

    # Test login
    response = client.post('/auth/login', data={
        'phone_number': '1112223333',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data # Should be on the dashboard after login

    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out.' in response.data

def test_route_protection(client, app):
    # 1. Test accessing without being logged in
    response = client.get('/admin/roles', follow_redirects=True)
    assert b'Sign In' in response.data # Should be redirected to login

    # 2. Setup users and roles for permission test
    with app.app_context():
        # Create a permission and a role
        perm = Permission(name='manage_roles')
        admin_role = Role(name='TestAdmin')
        admin_role.permissions.append(perm)
        db.session.add_all([perm, admin_role])

        # Create an admin user
        admin_user = User(first_name='test_admin', last_name='user', phone_number='admin123', password='password')
        admin_user.roles.append(admin_role)

        # Create a regular user
        regular_user = User(first_name='test_regular', last_name='user', phone_number='regular123', password='password')

        db.session.add_all([admin_user, regular_user])
        db.session.commit()

    # 3. Test as regular user (should get 403)
    client.post('/auth/login', data={'phone_number': 'regular123', 'password': 'password'})
    response = client.get('/admin/roles')
    assert response.status_code == 403 # Forbidden
    client.get('/auth/logout')

    # 4. Test as admin user (should get 200)
    client.post('/auth/login', data={'phone_number': 'admin123', 'password': 'password'})
    response = client.get('/admin/roles')
    assert response.status_code == 200
    assert b'Manage Roles' in response.data
    client.get('/auth/logout')

def test_temp_code_workflow(client, app):
    # 1. Setup
    with app.app_context():
        p_sensitive = Permission.query.filter_by(name='view_sensitive_data').first()
        if not p_sensitive:
            p_sensitive = Permission(name='view_sensitive_data')
            db.session.add(p_sensitive)

        p_admin = Permission.query.filter_by(name='manage_temp_codes').first()
        if not p_admin:
            p_admin = Permission(name='manage_temp_codes')
            db.session.add(p_admin)

        admin_role = Role(name='TempCodeAdmin')
        admin_role.permissions.append(p_admin)
        db.session.add(admin_role)

        admin = User(first_name='temp_admin', last_name='user', phone_number='tempadmin123', password='password')
        admin.roles.append(admin_role)

        user = User(first_name='temp_user', last_name='user', phone_number='tempuser123', password='password')
        db.session.add_all([admin, user])
        db.session.commit()
        user_id = user.id
        perm_id = p_sensitive.id

    # 2. User fails to access sensitive data
    client.post('/auth/login', data={'phone_number': 'tempuser123', 'password': 'password'})
    response = client.get('/sensitive_data')
    assert response.status_code == 403
    client.get('/auth/logout')

    # 3. Admin generates a code for the user
    client.post('/auth/login', data={'phone_number': 'tempadmin123', 'password': 'password'})
    response = client.post('/admin/temp_codes', data={
        'user': user_id,
        'permission': perm_id,
        'duration': 10,
        'is_single_use': True
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'New temporary access code generated' in response.data
    client.get('/auth/logout')

    # 4. Get the generated code from the DB
    with app.app_context():
        temp_code = TemporaryAccessCode.query.filter_by(user_id=user_id).first()
        assert temp_code is not None
        code_str = temp_code.code

    # 5. User activates the code and accesses the page
    client.post('/auth/login', data={'phone_number': 'tempuser123', 'password': 'password'})
    response = client.post('/activate_code', data={
        'temp_code': code_str,
        'next_url': '/sensitive_data'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'This is sensitive data.' in response.data
    client.get('/auth/logout')
