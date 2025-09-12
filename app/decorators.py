from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(permission_name):
    """
    Restricts access to routes to users with the required permission.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401) # Unauthorized
            if not current_user.has_permission(permission_name):
                abort(403) # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator
