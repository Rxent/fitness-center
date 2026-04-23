from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'gender', 'date_of_birth', 'age',
        'registration_date', 'is_active',
    )
    list_filter = ('gender', 'is_active', 'registration_date')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'user__email', 'user__phone', 'address',
    )
    autocomplete_fields = ('user',)
    readonly_fields = ('registration_date',)
    list_select_related = ('user',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',),
        }),
        ('Личные данные', {
            'fields': ('date_of_birth', 'gender', 'address', 'emergency_contact'),
        }),
        ('Здоровье', {
            'fields': ('health_notes',),
        }),
        ('Статус', {
            'fields': ('is_active', 'registration_date'),
        }),
    )

    @admin.display(description='Возраст')
    def age(self, obj):
        return obj.age
