from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Payment, Subscription, SubscriptionPlan


def plan_list(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    return render(request, 'subscriptions/plan_list.html', {'plans': plans})


def plan_detail(request, pk: int):
    plan = get_object_or_404(SubscriptionPlan, pk=pk, is_active=True)
    active_sub = None
    if request.user.is_authenticated and request.user.role == 'client':
        client = getattr(request.user, 'client_profile', None)
        if client:
            active_sub = Subscription.objects.filter(
                client=client, status='active',
                end_date__gte=timezone.now().date(),
            ).first()
    return render(request, 'subscriptions/plan_detail.html', {
        'plan': plan,
        'active_sub': active_sub,
    })


@login_required
@require_POST
def purchase_plan(request, pk: int):
    if request.user.role != 'client':
        return HttpResponseForbidden('Оформить абонемент может только клиент.')
    plan = get_object_or_404(SubscriptionPlan, pk=pk, is_active=True)
    client = getattr(request.user, 'client_profile', None)
    if not client:
        messages.error(request, 'Профиль клиента не настроен.')
        return redirect('subscriptions:plan_list')

    today = timezone.now().date()
    if Subscription.objects.filter(
        client=client, status='active', end_date__gte=today,
    ).exists():
        messages.warning(request, 'У вас уже есть действующий абонемент.')
        return redirect('subscriptions:my')

    sub = Subscription.objects.create(
        client=client, plan=plan, start_date=today, status='active',
    )
    method = request.POST.get('method', 'card')
    valid_methods = {key for key, _ in Payment.METHOD_CHOICES}
    if method not in valid_methods:
        method = 'card'
    Payment.objects.create(subscription=sub, amount=plan.price, method=method)
    messages.success(
        request,
        f'Абонемент «{plan.name}» оформлен до {sub.end_date:%d.%m.%Y}.',
    )
    return redirect('subscriptions:my')


@login_required
def my_subscriptions(request):
    if request.user.role != 'client':
        return redirect('users:dashboard')
    client = getattr(request.user, 'client_profile', None)
    subs = Subscription.objects.select_related('plan', 'payment').filter(
        client=client,
    ).order_by('-start_date')
    return render(request, 'subscriptions/my_subscriptions.html', {
        'subscriptions': subs,
    })
