from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def _check_role(view_func, allowed_roles):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.role in allowed_roles:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied('Недостаточно прав.')
    return wrapper


def admin_required(view_func):
    return _check_role(view_func, ['admin'])


def trainer_required(view_func):
    return _check_role(view_func, ['trainer'])


def client_required(view_func):
    return _check_role(view_func, ['client'])


def staff_required(view_func):
    return _check_role(view_func, ['admin', 'trainer'])
