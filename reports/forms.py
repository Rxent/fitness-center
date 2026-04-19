from django import forms
from django.utils import timezone

from subscriptions.models import SubscriptionPlan
from trainers.models import Trainer


class DateRangeForm(forms.Form):

    date_from = forms.DateField(
        label='С',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    date_to = forms.DateField(
        label='По',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )

    def defaults_last_month(self):
        today = timezone.now().date()
        self.initial.setdefault('date_to', today)
        self.initial.setdefault('date_from', today - timezone.timedelta(days=30))


class AttendanceFilterForm(DateRangeForm):

    trainer = forms.ModelChoiceField(
        label='Тренер',
        queryset=Trainer.objects.select_related('user'),
        required=False,
        empty_label='— все тренеры —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class RevenueFilterForm(DateRangeForm):

    plan = forms.ModelChoiceField(
        label='Тариф',
        queryset=SubscriptionPlan.objects.all(),
        required=False,
        empty_label='— все тарифы —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class TrainerLoadFilterForm(DateRangeForm):
    pass
