from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import ClientRegistrationForm, UserProfileForm


def home(request):
    """Главная страница — публичная, с призывом войти/зарегистрироваться."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'home.html')


def register(request):
    """Регистрация нового клиента."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать.')
            return redirect('users:dashboard')
    else:
        form = ClientRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard(request):
    """Роутер дашборда по роли пользователя."""
    user = request.user
    if user.is_superuser or user.role == 'admin':
        return _admin_dashboard(request)
    if user.role == 'trainer':
        return _trainer_dashboard(request)
    return _client_dashboard(request)


def _admin_dashboard(request):
    from clients.models import Client
    from schedule.models import TrainingClass
    from subscriptions.models import Payment, Subscription
    from trainers.models import Trainer

    today = timezone.now().date()
    context = {
        'clients_count': Client.objects.filter(is_active=True).count(),
        'trainers_count': Trainer.objects.filter(is_active=True).count(),
        'active_subscriptions': Subscription.objects.filter(
            status='active', end_date__gte=today,
        ).count(),
        'upcoming_classes': TrainingClass.objects.filter(
            start_time__gte=timezone.now(), status='scheduled',
        ).order_by('start_time')[:5],
        'recent_payments': Payment.objects.select_related(
            'subscription__client__user',
        ).order_by('-paid_at')[:5],
    }
    return render(request, 'users/dashboard_admin.html', context)


def _trainer_dashboard(request):
    from schedule.models import TrainingClass

    trainer = getattr(request.user, 'trainer_profile', None)
    now = timezone.now()
    classes = TrainingClass.objects.none()
    if trainer:
        classes = TrainingClass.objects.filter(
            trainer=trainer, start_time__gte=now,
        ).order_by('start_time')
    return render(request, 'users/dashboard_trainer.html', {
        'trainer': trainer,
        'upcoming_classes': classes[:10],
    })


def _client_dashboard(request):
    from schedule.models import Enrollment
    from subscriptions.models import Subscription

    client = getattr(request.user, 'client_profile', None)
    today = timezone.now().date()
    subscriptions = []
    enrollments = []
    if client:
        subscriptions = Subscription.objects.select_related('plan').filter(
            client=client,
        ).order_by('-start_date')[:5]
        enrollments = Enrollment.objects.select_related(
            'training_class__trainer__user', 'training_class__room',
        ).filter(
            client=client, training_class__start_time__gte=timezone.now(),
        ).order_by('training_class__start_time')[:10]
    active_subscription = next(
        (s for s in subscriptions if s.status == 'active' and s.end_date >= today),
        None,
    )
    return render(request, 'users/dashboard_client.html', {
        'client': client,
        'subscriptions': subscriptions,
        'active_subscription': active_subscription,
        'enrollments': enrollments,
    })


@login_required
def profile(request):
    """Редактирование собственного профиля."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect(reverse('users:profile'))
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})
