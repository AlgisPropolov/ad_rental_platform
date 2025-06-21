from django.shortcuts import render
from core.models import Client

def list_clients_view(request):
    query = request.GET.get('q', '')
    clients = Client.objects.all()
    if query:
        clients = clients.filter(name__icontains=query)
    return render(request, 'core/list_clients.html', {'clients': clients, 'query': query})
