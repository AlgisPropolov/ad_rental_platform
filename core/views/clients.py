from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Prefetch, Count
from core.models import Client, Deal, Contract
from core.forms import ClientForm


class ClientBaseView:
    """Базовый класс для наследования всех Client views"""
    model = Client
    context_object_name = 'client'

    def get_success_url(self):
        return reverse_lazy('core:client-list')


class ClientListView(ClientBaseView, ListView):
    template_name = 'core/clients/list.html'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        return super().get_queryset().annotate(
            deals_count=Count('deals', distinct=True)  # Исправлено: заменено annotate_deals_count()
        ).only(
            'id', 'name', 'inn', 'contact_person', 'created_at'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clients'] = self.get_queryset().count()
        return context


class ClientCreateView(ClientBaseView, CreateView):
    form_class = ClientForm
    template_name = 'core/clients/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Клиент успешно создан')
        return response


class ClientDetailView(ClientBaseView, DetailView):
    template_name = 'core/clients/detail.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch('deals', queryset=Deal.objects.only('id', 'title', 'status')),
            Prefetch('contracts', queryset=Contract.objects.only('id', 'number', 'start_date'))
        )


class ClientUpdateView(ClientBaseView, UpdateView):
    form_class = ClientForm
    template_name = 'core/clients/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Данные клиента обновлены')
        return response


class ClientDeleteView(ClientBaseView, DeleteView):
    template_name = 'core/clients/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        client = self.get_object()

        # Проверка на наличие связанных договоров
        if client.contracts.exists():
            messages.error(
                request,
                'Нельзя удалить клиента с привязанными договорами'
            )
            return redirect('core:client-detail', pk=client.pk)

        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Клиент успешно удален')
        return response