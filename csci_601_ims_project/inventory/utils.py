from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # ✅ Redirect to login if not authenticated

            # ✅ Handle missing or invalid roles gracefully
            user_role = getattr(request.user, 'role', None)  # Avoid AttributeError

            if user_role and user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied  # ✅ Show 403 Forbidden error if unauthorized

        return wrapper
    return decorator
