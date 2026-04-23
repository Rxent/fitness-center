from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'role', 'phone', 'is_active', 'is_staff',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Профиль фитнес-центра'), {
            'fields': ('role', 'phone', 'photo'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Профиль фитнес-центра'), {
            'fields': ('role', 'phone', 'email', 'first_name', 'last_name'),
        }),
    )
