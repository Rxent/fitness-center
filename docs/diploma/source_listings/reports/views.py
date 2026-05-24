"""View-функции отчётов.

Каждый отчёт берёт фильтры из GET-формы, зовёт функцию из services.py
и рендерит HTML-страницу с таблицей.

Все страницы доступны только администратору через @admin_required.
"""
from django.shortcuts import render

from users.decorators import admin_required

from . import services
from .forms import (
    AttendanceFilterForm,
    RevenueFilterForm,
    TrainerLoadFilterForm,
)


@admin_required
def report_index(request):
    """Страница со списком доступных отчётов."""
    return render(request, 'reports/index.html')


@admin_required
def attendance(request):
    """Отчёт по посещаемости тренировок."""
    form = AttendanceFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.attendance_report(
        data.get('date_from'), data.get('date_to'), data.get('trainer'),
    )
    return render(request, 'reports/attendance.html', {'form': form, 'report': report})


@admin_required
def revenue(request):
    """Отчёт по выручке."""
    form = RevenueFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.revenue_report(
        data.get('date_from'), data.get('date_to'), data.get('plan'),
    )
    return render(request, 'reports/revenue.html', {'form': form, 'report': report})


@admin_required
def trainer_load(request):
    """Отчёт по загрузке тренеров."""
    form = TrainerLoadFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.trainer_load_report(
        data.get('date_from'), data.get('date_to'),
    )
    return render(request, 'reports/trainer_load.html', {'form': form, 'report': report})
