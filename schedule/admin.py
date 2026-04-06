from django.contrib import admin

from .models import Enrollment, GymRoom, TrainingClass


@admin.register(GymRoom)
class GymRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'description')
    search_fields = ('name', 'description')


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ('client',)
    readonly_fields = ('enrolled_at',)


@admin.register(TrainingClass)
class TrainingClassAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'trainer', 'room', 'start_time', 'end_time',
        'max_participants', 'status',
    )
    list_filter = ('status', 'room', 'trainer', 'start_time')
    search_fields = (
        'name', 'description', 'trainer__user__first_name',
        'trainer__user__last_name',
    )
    autocomplete_fields = ('trainer', 'room')
    date_hierarchy = 'start_time'
    inlines = [EnrollmentInline]
    list_select_related = ('trainer__user', 'room')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'training_class', 'status', 'enrolled_at')
    list_filter = ('status', 'enrolled_at')
    search_fields = (
        'client__user__username', 'client__user__first_name',
        'client__user__last_name', 'training_class__name',
    )
    autocomplete_fields = ('client', 'training_class')
    readonly_fields = ('enrolled_at',)
