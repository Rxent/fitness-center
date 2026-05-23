from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import admin_required

from .forms import ClientForm
from .models import Client


@admin_required
def client_list(request):
    query = request.GET.get('q', '').strip()
    clients = Client.objects.select_related('user').order_by('user__last_name', 'user__first_name')
    if query:
        clients = clients.filter(user__last_name__icontains=query) | clients.filter(
            user__first_name__icontains=query,
        ) | clients.filter(user__phone__icontains=query)
    return render(request, 'clients/client_list.html', {'clients': clients, 'query': query})


@admin_required
def client_update(request, pk):
    client = get_object_or_404(Client.objects.select_related('user'), pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Карточка клиента обновлена.')
            return redirect('clients:client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form, 'client': client})
