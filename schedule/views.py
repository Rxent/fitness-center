from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from subscriptions.models import Subscription
from trainers.models import Trainer
from users.decorators import trainer_required

from .models import Enrollment, GymRoom, TrainingClass


def class_list(request):
    """Список предстоящих тренировок с фильтрами."""
    qs = TrainingClass.objects.select_related(
        'trainer__user', 'room',
    ).filter(start_time__gte=timezone.now()).annotate(
        taken=Count('enrollments'),
    )

    trainer_id = request.GET.get('trainer')
    if trainer_id:
        qs = qs.filter(trainer_id=trainer_id)
    room_id = request.GET.get('room')
    if room_id:
        qs = qs.filter(room_id=room_id)
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)
    date_from = request.GET.get('date_from')
    if date_from:
        qs = qs.filter(start_time__date__gte=date_from)
    date_to = request.GET.get('date_to')
    if date_to:
        qs = qs.filter(start_time__date__lte=date_to)

    qs = qs.order_by('start_time')

    enrolled_ids = set()
    if request.user.is_authenticated and request.user.role == 'client':
        client = getattr(request.user, 'client_profile', None)
        if client:
            enrolled_ids = set(
                Enrollment.objects.filter(
                    client=client,
                    training_class__in=qs,
                ).exclude(status='cancelled').values_list(
                    'training_class_id', flat=True,
                )
            )

    context = {
        'classes': qs,
        'trainers': Trainer.objects.filter(is_active=True).select_related('user'),
        'rooms': GymRoom.objects.all(),
        'statuses': TrainingClass.STATUS_CHOICES,
        'filters': {
            'trainer': trainer_id or '',
            'room': room_id or '',
            'status': status or '',
            'date_from': date_from or '',
            'date_to': date_to or '',
        },
        'enrolled_ids': enrolled_ids,
    }
    return render(request, 'schedule/class_list.html', context)


def class_detail(request, pk: int):
    tc = get_object_or_404(
        TrainingClass.objects.select_related('trainer__user', 'room'),
        pk=pk,
    )
    enrollment = None
    can_enroll, reason = False, ''
    if request.user.is_authenticated and request.user.role == 'client':
        client = getattr(request.user, 'client_profile', None)
        if client:
            enrollment = Enrollment.objects.filter(
                client=client, training_class=tc,
            ).first()
            can_enroll, reason = _can_enroll(client, tc, enrollment)
    return render(request, 'schedule/class_detail.html', {
        'tc': tc,
        'enrollment': enrollment,
        'can_enroll': can_enroll,
        'cant_enroll_reason': reason,
        'is_future': tc.start_time > timezone.now(),
        'enrollments': tc.enrollments.select_related('client__user').all()
            if _can_see_enrollments(request.user, tc) else [],
    })


def _can_see_enrollments(user, tc):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role == 'admin':
        return True
    return user.role == 'trainer' and tc.trainer_id and tc.trainer.user_id == user.id


def _can_enroll(client, tc: TrainingClass, enrollment: Enrollment | None):
    if tc.start_time <= timezone.now():
        return False, 'Тренировка уже началась или завершена.'
    if tc.status != 'scheduled':
        return False, f'Тренировка имеет статус «{tc.get_status_display()}».'
    if enrollment and enrollment.status != 'cancelled':
        return False, 'Вы уже записаны на эту тренировку.'
    if tc.is_full:
        return False, 'Свободных мест нет.'
    today = timezone.now().date()
    has_active_sub = Subscription.objects.filter(
        client=client, status='active', end_date__gte=today,
    ).exists()
    if not has_active_sub:
        return False, 'Для записи нужен действующий абонемент.'
    return True, ''


@login_required
@require_POST
def enroll(request, pk: int):
    if request.user.role != 'client':
        return HttpResponseForbidden('Запись доступна только клиентам.')
    client = getattr(request.user, 'client_profile', None)
    if not client:
        messages.error(request, 'Профиль клиента не настроен.')
        return redirect('schedule:class_detail', pk=pk)

    tc = get_object_or_404(TrainingClass, pk=pk)
    existing = Enrollment.objects.filter(client=client, training_class=tc).first()
    can, reason = _can_enroll(client, tc, existing)
    if not can:
        messages.error(request, reason)
        return redirect('schedule:class_detail', pk=pk)

    if existing:
        existing.status = 'enrolled'
        existing.save(update_fields=['status'])
    else:
        Enrollment.objects.create(client=client, training_class=tc)
    messages.success(request, f'Вы записаны на «{tc.name}».')
    return redirect('schedule:class_detail', pk=pk)


@login_required
@require_POST
def cancel_enrollment(request, pk: int):
    if request.user.role != 'client':
        return HttpResponseForbidden()
    client = getattr(request.user, 'client_profile', None)
    enrollment = get_object_or_404(
        Enrollment, training_class_id=pk, client=client,
    )
    if enrollment.training_class.start_time <= timezone.now():
        messages.error(request, 'Тренировка уже началась, отмена невозможна.')
    else:
        enrollment.status = 'cancelled'
        enrollment.save(update_fields=['status'])
        messages.success(request, 'Запись отменена.')
    return redirect('schedule:my_enrollments')


@login_required
def my_enrollments(request):
    """Страница клиента: все его записи (будущие и прошедшие)."""
    if request.user.role != 'client':
        return redirect('users:dashboard')
    client = getattr(request.user, 'client_profile', None)
    qs = Enrollment.objects.select_related(
        'training_class__trainer__user', 'training_class__room',
    ).filter(client=client).order_by('-training_class__start_time')
    now = timezone.now()
    upcoming = [e for e in qs if e.training_class.start_time >= now]
    past = [e for e in qs if e.training_class.start_time < now]
    return render(request, 'schedule/my_enrollments.html', {
        'upcoming': upcoming,
        'past': past,
    })


@trainer_required
def trainer_classes(request):
    """Страница тренера: его тренировки с возможностью управления."""
    trainer = getattr(request.user, 'trainer_profile', None)
    if not trainer:
        return redirect('users:dashboard')
    qs = TrainingClass.objects.filter(trainer=trainer).annotate(
        taken=Count('enrollments'),
    ).order_by('-start_time')
    status = request.GET.get('status', 'all')
    if status != 'all':
        qs = qs.filter(status=status)
    return render(request, 'schedule/trainer_classes.html', {
        'classes': qs,
        'status_filter': status,
        'statuses': TrainingClass.STATUS_CHOICES,
    })


@trainer_required
def trainer_class_detail(request, pk: int):
    trainer = request.user.trainer_profile
    tc = get_object_or_404(TrainingClass, pk=pk, trainer=trainer)
    enrollments = tc.enrollments.select_related('client__user').all()
    return render(request, 'schedule/trainer_class_detail.html', {
        'tc': tc,
        'enrollments': enrollments,
        'statuses': TrainingClass.STATUS_CHOICES,
        'enrollment_statuses': Enrollment.STATUS_CHOICES,
    })


@trainer_required
@require_POST
def mark_class_status(request, pk: int):
    trainer = request.user.trainer_profile
    tc = get_object_or_404(TrainingClass, pk=pk, trainer=trainer)
    new_status = request.POST.get('status')
    valid = {key for key, _ in TrainingClass.STATUS_CHOICES}
    if new_status in valid:
        tc.status = new_status
        tc.save(update_fields=['status'])
        messages.success(request, f'Статус тренировки: {tc.get_status_display()}.')
    return redirect('schedule:trainer_class_detail', pk=pk)


@trainer_required
@require_POST
def mark_enrollment_status(request, enrollment_id: int):
    trainer = request.user.trainer_profile
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('training_class'),
        pk=enrollment_id, training_class__trainer=trainer,
    )
    new_status = request.POST.get('status')
    valid = {key for key, _ in Enrollment.STATUS_CHOICES}
    if new_status in valid:
        enrollment.status = new_status
        enrollment.save(update_fields=['status'])
        # при отметке «посетил» увеличиваем счётчик посещений активного абонемента
        if new_status == 'attended':
            active = Subscription.objects.filter(
                client=enrollment.client, status='active',
                start_date__lte=enrollment.training_class.start_time.date(),
                end_date__gte=enrollment.training_class.start_time.date(),
            ).first()
            if active:
                active.visits_used += 1
                active.save(update_fields=['visits_used'])
        messages.success(request, 'Статус записи обновлён.')
    return redirect(
        'schedule:trainer_class_detail', pk=enrollment.training_class_id,
    )
