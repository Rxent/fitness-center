from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from clients.models import Client
from schedule.models import Enrollment, TrainingClass
from subscriptions.models import Payment, Subscription
from trainers.models import Trainer

from .forms import ClientRegistrationForm, UserProfileForm


def home(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'home.html')


def register(request):
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
    user = request.user
    if user.is_superuser or user.role == 'admin':
        return admin_dashboard(request)
    if user.role == 'trainer':
        return trainer_dashboard(request)
    return client_dashboard(request)


def admin_dashboard(request):
    today = timezone.now().date()
    now = timezone.now()
    context = {
        'clients_count': Client.objects.filter(is_active=True).count(),
        'trainers_count': Trainer.objects.filter(is_active=True).count(),
        'active_subscriptions': Subscription.objects.filter(
            status='active', end_date__gte=today,
        ).count(),
        'upcoming_classes': TrainingClass.objects.filter(
            start_time__gte=now, status='scheduled',
        ).order_by('start_time')[:5],
        'recent_payments': Payment.objects.select_related(
            'subscription__client__user',
        ).order_by('-paid_at')[:5],
    }
    return render(request, 'users/dashboard_admin.html', context)


def trainer_dashboard(request):
    trainer = getattr(request.user, 'trainer_profile', None)
    classes = []
    if trainer:
        classes = TrainingClass.objects.filter(
            trainer=trainer, start_time__gte=timezone.now(),
        ).order_by('start_time')[:10]
    return render(request, 'users/dashboard_trainer.html', {
        'trainer': trainer,
        'upcoming_classes': classes,
    })


def client_dashboard(request):
    client = getattr(request.user, 'client_profile', None)
    today = timezone.now().date()
    subscriptions = []
    enrollments = []
    active_subscription = None
    if client:
        subscriptions = list(Subscription.objects.select_related('plan').filter(
            client=client,
        ).order_by('-start_date')[:5])
        enrollments = Enrollment.objects.select_related(
            'training_class__trainer__user', 'training_class__room',
        ).filter(
            client=client, training_class__start_time__gte=timezone.now(),
        ).order_by('training_class__start_time')[:10]
        for s in subscriptions:
            if s.status == 'active' and s.end_date >= today:
                active_subscription = s
                break
    return render(request, 'users/dashboard_client.html', {
        'client': client,
        'subscriptions': subscriptions,
        'active_subscription': active_subscription,
        'enrollments': enrollments,
    })


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect(reverse('users:profile'))
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})
