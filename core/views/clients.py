from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from core.models import Client
from core.forms import ClientForm

class ClientListView(ListView):
    model = Client
    template_name = 'clients/list.html'
    context_object_name = 'clients'
    paginate_by = 20
    ordering = ['-created_at']

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/create.html'
    success_url = reverse_lazy('client-list')

    def form_valid(self, form):
        messages.success(self.request, 'Клиент успешно создан')
        return super().form_valid(form)

class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        return Client.objects.select_related('user')

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/update.html'
    success_url = reverse_lazy('client-list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные клиента обновлены')
        return super().form_valid(form)

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/delete.html'
    success_url = reverse_lazy('client-list')
    context_object_name = 'client'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Клиент успешно удален')
        return super().delete(request, *args, **kwargs)