from django.contrib import admin

from .models import Payment, Subscription, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'plan_type', 'duration_days', 'visits_limit',
        'price', 'is_active',
    )
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('paid_at',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'client', 'plan', 'start_date', 'end_date',
        'visits_used', 'status', 'created_at',
    )
    list_filter = ('status', 'plan__plan_type', 'start_date', 'end_date')
    search_fields = (
        'client__user__username', 'client__user__first_name',
        'client__user__last_name', 'plan__name',
    )
    autocomplete_fields = ('client', 'plan')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at',)
    inlines = [PaymentInline]
    list_select_related = ('client__user', 'plan')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'method', 'paid_at')
    list_filter = ('method', 'paid_at')
    search_fields = (
        'subscription__client__user__username',
        'subscription__client__user__first_name',
        'subscription__client__user__last_name',
    )
    autocomplete_fields = ('subscription',)
    date_hierarchy = 'paid_at'
    readonly_fields = ('paid_at',)
