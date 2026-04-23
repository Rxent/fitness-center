from django.shortcuts import get_object_or_404, render

from .models import Specialization, Trainer


def trainer_list(request):
    qs = Trainer.objects.filter(is_active=True).select_related('user').prefetch_related('specializations')
    spec_id = request.GET.get('specialization')
    if spec_id:
        qs = qs.filter(specializations__id=spec_id).distinct()
    return render(request, 'trainers/trainer_list.html', {
        'trainers': qs,
        'specializations': Specialization.objects.all(),
        'active_spec': int(spec_id) if spec_id and spec_id.isdigit() else None,
    })


def trainer_detail(request, pk: int):
    trainer = get_object_or_404(
        Trainer.objects.select_related('user').prefetch_related('specializations'),
        pk=pk, is_active=True,
    )
    from django.utils import timezone
    from schedule.models import TrainingClass

    upcoming = TrainingClass.objects.filter(
        trainer=trainer,
        start_time__gte=timezone.now(),
        status='scheduled',
    ).select_related('room').order_by('start_time')[:10]
    return render(request, 'trainers/trainer_detail.html', {
        'trainer': trainer,
        'upcoming_classes': upcoming,
    })
