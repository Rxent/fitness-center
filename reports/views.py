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
    return render(request, 'reports/index.html')


@admin_required
def attendance(request):
    form = AttendanceFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.attendance_report(
        data.get('date_from'), data.get('date_to'), data.get('trainer'),
    )
    return render(request, 'reports/attendance.html', {'form': form, 'report': report})


@admin_required
def revenue(request):
    form = RevenueFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.revenue_report(
        data.get('date_from'), data.get('date_to'), data.get('plan'),
    )
    return render(request, 'reports/revenue.html', {'form': form, 'report': report})


@admin_required
def trainer_load(request):
    form = TrainerLoadFilterForm(request.GET or None)
    data = form.cleaned_data if form.is_valid() else {}
    report = services.trainer_load_report(
        data.get('date_from'), data.get('date_to'),
    )
    return render(request, 'reports/trainer_load.html', {'form': form, 'report': report})
