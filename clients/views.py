from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from users.decorators import staff_required

from .models import Client


@staff_required
def client_list(request):
    qs = Client.objects.filter(is_active=True).select_related('user').order_by(
        'user__last_name', 'user__first_name',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__email__icontains=q)
        ).distinct()
    return render(request, 'clients/client_list.html', {
        'clients': qs, 'query': q,
    })


@staff_required
def client_detail(request, pk: int):
    client = get_object_or_404(
        Client.objects.select_related('user'), pk=pk,
    )
    subs = client.subscriptions.select_related('plan').order_by('-start_date')[:10]
    enrollments = client.enrollments.select_related(
        'training_class__trainer__user',
    ).order_by('-training_class__start_time')[:10]
    return render(request, 'clients/client_detail.html', {
        'client': client,
        'subscriptions': subs,
        'enrollments': enrollments,
    })
