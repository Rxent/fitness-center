"""View-функции отчётов.

Для каждого отчёта одна view делает три вещи:
1) валидирует GET-форму с фильтрами;
2) зовёт функцию из services.py, получает словарь отчёта;
3) если ?format=xlsx или ?format=pdf — отдаёт файл; иначе рендерит HTML.

Все страницы доступны только администратору через @admin_required.
"""
from django.shortcuts import render

from users.decorators import admin_required

from . import exporters, services
from .forms import (
    AttendanceFilterForm,
    RevenueFilterForm,
    TrainerLoadFilterForm,
)


def _render_or_export(request, form, report: dict, template: str, filename: str):
    """Общий выход: HTML, PDF или Excel — в зависимости от ?format=.

    Выделено в функцию, чтобы не повторять один и тот же switch во всех трёх
    view-функциях отчётов.
    """
    fmt = request.GET.get('format')
    if fmt == 'xlsx':
        return exporters.to_excel(report, filename)
    if fmt == 'pdf':
        return exporters.to_pdf(report, filename)
    return render(request, template, {'form': form, 'report': report})


@admin_required
def report_index(request):
    """Страница со списком доступных отчётов."""
    return render(request, 'reports/index.html')


@admin_required
def attendance(request):
    """Отчёт по посещаемости тренировок."""
    form = AttendanceFilterForm(request.GET or None)
    # В форме все поля необязательные. Достаём cleaned_data только если всё валидно,
    # иначе работаем со значениями по умолчанию (последние 30 дней).
    data = form.cleaned_data if form.is_valid() else {}
    report = services.attendance_report(
        data.get('date_from'), data.get('date_to'), data.get('trainer'),
    )
    return _render_or_export(request, form, report, 'reports/attendance.html', 'attendance')


@admin_required
def revenue(request):
    """Отчёт по выручке."""
    form = RevenueFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.revenue_report(
        data.get('date_from'), data.get('date_to'), data.get('plan'),
    )
    return _render_or_export(request, form, report, 'reports/revenue.html', 'revenue')


@admin_required
def trainer_load(request):
    """Отчёт по загрузке тренеров."""
    form = TrainerLoadFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.trainer_load_report(
        data.get('date_from'), data.get('date_to'),
    )
    return _render_or_export(request, form, report, 'reports/trainer_load.html', 'trainer_load')
