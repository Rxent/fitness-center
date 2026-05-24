from django.contrib import admin

from .models import Specialization, Trainer


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'experience_years', 'hourly_rate',
        'hired_date', 'is_active',
    )
    list_filter = ('is_active', 'specializations', 'hired_date')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'bio',
    )
    autocomplete_fields = ('user',)
    filter_horizontal = ('specializations',)
    readonly_fields = ('hired_date',)
    list_select_related = ('user',)
