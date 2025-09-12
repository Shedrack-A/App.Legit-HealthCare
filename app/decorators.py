from functools import wraps
from flask import abort, session
from flask_login import current_user
from datetime import datetime

def permission_required(permission_name):
    """
    Restricts access to routes to users with the required permission.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401) # Unauthorized

            # Check for temporary permissions first
            if 'temp_permissions' in session:
                temp_perm = session['temp_permissions'].get(permission_name)
                if temp_perm:
                    expiry_time = datetime.fromisoformat(temp_perm)
                    if expiry_time > datetime.utcnow():
                        return f(*args, **kwargs) # Temporary permission is valid

            # If no valid temporary permission, check permanent permissions
            if not current_user.has_permission(permission_name):
                abort(403) # Forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator
