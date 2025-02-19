from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles=None):  # ✅ Use `None` instead of mutable default list
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # ✅ Redirect to login if not authenticated

            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied  # ✅ Show 403 Forbidden error if unauthorized

        return wrapper
    return decorator  # ✅ Ensure the decorator function is returned properly


# def role_required(allowed_roles=None):
#     if allowed_roles is None:
#         allowed_roles = []

#     def decorator(view_func):
#         @wraps(view_func)
#         def wrapper(request, *args, **kwargs):
#             if not request.user or not request.user.is_authenticated:
#                 return redirect('login')  # ✅ Redirect to login if not authenticated

#             # ✅ Safely get user role to avoid AttributeError
#             user_role = getattr(request.user, 'role', None)  

#             if user_role in allowed_roles:
#                 return view_func(request, *args, **kwargs)

#             raise PermissionDenied  # ✅ Show 403 Forbidden error if unauthorized

#         return wrapper
#     return decorator