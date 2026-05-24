"""
Декораторы для ограничения доступа к страницам по роли пользователя.

Использование:
    @admin_required
    def my_view(request): ...

Декоратор оборачивает view-функцию и перед её вызовом проверяет:
1) пользователь вошёл в систему (через встроенный @login_required);
2) роль пользователя совпадает с одной из разрешённых, либо он суперюзер.

Если проверка не прошла — Django возвращает страницу 403 Forbidden
(PermissionDenied).
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Возвращает декоратор, пропускающий только указанные роли (и суперюзера)."""

    def decorator(view_func):
        # @wraps нужен, чтобы Django корректно видел имя и docstring
        # исходной view-функции, а не обёртки.
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            # Суперюзер имеет доступ всегда (это удобно для администратора,
            # созданного через createsuperuser).
            if user.is_superuser or user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied('Недостаточно прав для доступа к этой странице.')

        return _wrapped

    return decorator


# Готовые декораторы для наиболее частых случаев — чтобы в коде было короче.
admin_required = role_required('admin')
trainer_required = role_required('trainer')
client_required = role_required('client')
# Общие страницы для персонала (админ + тренер), например список клиентов.
staff_required = role_required('admin', 'trainer')
