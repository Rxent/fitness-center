"""Формы-фильтры для отчётов.

Здесь только поля для параметров отчёта: период, тренер, тариф.
Сами данные собираются в services.py, а отображение — в views.py.
"""
from django import forms
from django.utils import timezone

from subscriptions.models import SubscriptionPlan
from trainers.models import Trainer


class DateRangeForm(forms.Form):
    """Период с-по. Обе даты необязательные — можно считать за всё время."""

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
        """Подставить период «последние 30 дней», если поля пустые."""
        today = timezone.now().date()
        self.initial.setdefault('date_to', today)
        self.initial.setdefault('date_from', today - timezone.timedelta(days=30))


class AttendanceFilterForm(DateRangeForm):
    """Фильтр отчёта по посещаемости: период + (опц.) тренер."""

    trainer = forms.ModelChoiceField(
        label='Тренер',
        queryset=Trainer.objects.select_related('user'),
        required=False,
        empty_label='— все тренеры —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class RevenueFilterForm(DateRangeForm):
    """Фильтр отчёта по выручке: период + (опц.) тариф."""

    plan = forms.ModelChoiceField(
        label='Тариф',
        queryset=SubscriptionPlan.objects.all(),
        required=False,
        empty_label='— все тарифы —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class TrainerLoadFilterForm(DateRangeForm):
    """Фильтр отчёта по загрузке тренеров: только период."""
    pass
