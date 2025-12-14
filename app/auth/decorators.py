from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to ensure current user has one of the required roles.
    Usage: @role_required('admin', 'operator')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            
            if current_user.role not in roles and current_user.role != 'admin': 
                # Admin can generally access everything, or explicitly list 'admin' 
                #Logic: 'admin' role bypass checking if we want that, 
                # but better to be explicit in usage: @role_required('admin')
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
