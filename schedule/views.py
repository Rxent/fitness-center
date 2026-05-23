from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from users.decorators import admin_required, trainer_required

from .forms import TrainingClassForm
from .models import Enrollment, TrainingClass


def class_list(request):
    classes = TrainingClass.objects.select_related('trainer__user', 'room').filter(
        start_time__gte=timezone.now(), status='scheduled',
    ).order_by('start_time')
    enrolled_ids = set()
    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'client':
        client = getattr(request.user, 'client_profile', None)
        if client:
            enrolled_ids = set(Enrollment.objects.filter(
                client=client, status='enrolled', training_class__in=classes,
            ).values_list('training_class_id', flat=True))
    return render(request, 'schedule/class_list.html', {
        'classes': classes,
        'enrolled_ids': enrolled_ids,
    })


@login_required
def my_enrollments(request):
    client = getattr(request.user, 'client_profile', None)
    enrollments = Enrollment.objects.none()
    if client:
        enrollments = Enrollment.objects.select_related(
            'training_class__trainer__user', 'training_class__room',
        ).filter(client=client).order_by('-training_class__start_time')
    return render(request, 'schedule/my_enrollments.html', {'enrollments': enrollments})


@trainer_required
def trainer_schedule(request):
    trainer = getattr(request.user, 'trainer_profile', None)
    classes = TrainingClass.objects.none()
    if trainer:
        classes = TrainingClass.objects.select_related('room').prefetch_related(
            'enrollments__client__user',
        ).filter(trainer=trainer).order_by('start_time')
    return render(request, 'schedule/trainer_schedule.html', {'classes': classes})


@admin_required
def class_create(request):
    if request.method == 'POST':
        form = TrainingClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тренировка добавлена.')
            return redirect('schedule:class_list')
    else:
        form = TrainingClassForm()
    return render(request, 'schedule/class_form.html', {'form': form, 'title': 'Новая тренировка'})


@admin_required
def class_update(request, pk):
    training_class = get_object_or_404(TrainingClass, pk=pk)
    if request.method == 'POST':
        form = TrainingClassForm(request.POST, instance=training_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тренировка обновлена.')
            return redirect('schedule:class_list')
    else:
        form = TrainingClassForm(instance=training_class)
    return render(request, 'schedule/class_form.html', {'form': form, 'title': 'Редактирование тренировки'})


@login_required
def enroll(request, pk):
    if getattr(request.user, 'role', None) != 'client':
        messages.error(request, 'Записываться на тренировки могут только клиенты.')
        return redirect('schedule:class_list')
    training_class = get_object_or_404(TrainingClass, pk=pk, status='scheduled')
    client = getattr(request.user, 'client_profile', None)
    if not client:
        messages.error(request, 'Профиль клиента не найден.')
        return redirect('schedule:class_list')
    if training_class.is_full:
        messages.error(request, 'Свободных мест на тренировку нет.')
        return redirect('schedule:class_list')
    try:
        Enrollment.objects.create(client=client, training_class=training_class)
        messages.success(request, 'Вы записаны на тренировку.')
    except IntegrityError:
        messages.info(request, 'Вы уже записаны на эту тренировку.')
    return redirect('schedule:class_list')


@login_required
def cancel_enrollment(request, pk):
    client = getattr(request.user, 'client_profile', None)
    enrollment = get_object_or_404(Enrollment, pk=pk, client=client)
    enrollment.status = 'cancelled'
    enrollment.save(update_fields=['status'])
    messages.success(request, 'Запись отменена.')
    return redirect('schedule:my_enrollments')
