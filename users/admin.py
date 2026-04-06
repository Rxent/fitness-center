from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from clients.models import Client
from trainers.models import Trainer

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
        ('Профиль фитнес-центра', {'fields': ('role', 'phone', 'photo')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Профиль фитнес-центра', {
            'fields': ('role', 'phone', 'email', 'first_name', 'last_name'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.role == 'client':
            Client.objects.get_or_create(user=obj)
        elif obj.role == 'trainer':
            Trainer.objects.get_or_create(user=obj)
