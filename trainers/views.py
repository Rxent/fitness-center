from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import admin_required

from .forms import TrainerForm
from .models import Trainer


@admin_required
def trainer_list(request):
    trainers = Trainer.objects.select_related('user').prefetch_related('specializations').order_by(
        'user__last_name', 'user__first_name',
    )
    return render(request, 'trainers/trainer_list.html', {'trainers': trainers})


@admin_required
def trainer_update(request, pk):
    trainer = get_object_or_404(Trainer.objects.select_related('user'), pk=pk)
    if request.method == 'POST':
        form = TrainerForm(request.POST, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Карточка тренера обновлена.')
            return redirect('trainers:trainer_list')
    else:
        form = TrainerForm(instance=trainer)
    return render(request, 'trainers/trainer_form.html', {'form': form, 'trainer': trainer})
