from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Декоратор: доступ только для пользователей с одной из указанных ролей."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser or user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied('Недостаточно прав для доступа к этой странице.')

        return _wrapped

    return decorator


admin_required = role_required('admin')
trainer_required = role_required('trainer')
client_required = role_required('client')
staff_required = role_required('admin', 'trainer')
