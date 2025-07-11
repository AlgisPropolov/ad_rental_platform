from django.shortcuts import render, redirect
from django.views.generic import (
    ListView, CreateView, DetailView,
    UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from .models import (
    Client, Asset, AvailabilitySlot,
    Deal, Contract, Payment, DealTask
)


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Финансовая аналитика
        context['finance'] = {
            'total_income': Payment.objects.filter(is_confirmed=True).aggregate(Sum('amount'))['amount__sum'] or 0,
            'unpaid_amount': Contract.objects.filter(is_active=True).aggregate(Sum('total_amount'))[
                                 'total_amount__sum'] or 0
        }

        # Статистика по активам
        context['assets'] = {
            'total_assets': Asset.objects.count(),
            'used_assets': AvailabilitySlot.objects.filter(is_available=False).count(),
            'available_assets': AvailabilitySlot.objects.filter(is_available=True).count()
        }

        # Ближайшие задачи
        context['tasks'] = DealTask.objects.filter(
            is_done=False,
            due_date__lte=timezone.now() + timezone.timedelta(days=3)
        ).order_by('due_date')[:5]

        return context


class AnalyticsView(TemplateView):
    template_name = 'core/analytics.html'


class AvailabilityView(TemplateView):
    template_name = 'core/availability.html'


# Client Views
class ClientListView(ListView):
    model = Client
    template_name = 'core/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20
    ordering = ['-created_at']


class ClientCreateView(CreateView):
    model = Client
    fields = ['name', 'inn', 'contact_person', 'phone', 'email', 'is_vip', 'notes']
    template_name = 'core/client_form.html'
    success_url = reverse_lazy('core:client-list')

    def form_valid(self, form):
        messages.success(self.request, 'Клиент успешно создан')
        return super().form_valid(form)


class ClientDetailView(DetailView):
    model = Client
    template_name = 'core/client_detail.html'
    context_object_name = 'client'


class ClientUpdateView(UpdateView):
    model = Client
    fields = ['name', 'inn', 'contact_person', 'phone', 'email', 'is_vip', 'notes']
    template_name = 'core/client_form.html'
    success_url = reverse_lazy('core:client-list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные клиента обновлены')
        return super().form_valid(form)


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'core/client_confirm_delete.html'
    success_url = reverse_lazy('core:client-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Клиент удален')
        return super().delete(request, *args, **kwargs)


# Asset Views
class AssetListView(ListView):
    model = Asset
    template_name = 'core/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20
    ordering = ['name']


class AssetCreateView(CreateView):
    model = Asset
    fields = ['name', 'asset_type', 'zone', 'location', 'daily_rate', 'is_active', 'notes']
    template_name = 'core/asset_form.html'
    success_url = reverse_lazy('core:asset-list')

    def form_valid(self, form):
        messages.success(self.request, 'Актив успешно создан')
        return super().form_valid(form)


class AssetDetailView(DetailView):
    model = Asset
    template_name = 'core/asset_detail.html'
    context_object_name = 'asset'


class AssetUpdateView(UpdateView):
    model = Asset
    fields = ['name', 'asset_type', 'zone', 'location', 'daily_rate', 'is_active', 'notes']
    template_name = 'core/asset_form.html'
    success_url = reverse_lazy('core:asset-list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные актива обновлены')
        return super().form_valid(form)


class AssetDeleteView(DeleteView):
    model = Asset
    template_name = 'core/asset_confirm_delete.html'
    success_url = reverse_lazy('core:asset-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Актив удален')
        return super().delete(request, *args, **kwargs)


class AssetSlotsView(DetailView):
    model = Asset
    template_name = 'core/asset_slots.html'
    context_object_name = 'asset'


# Availability Slot Views
class AvailabilitySlotListView(ListView):
    model = AvailabilitySlot
    template_name = 'core/availability_slot_list.html'
    context_object_name = 'slots'
    ordering = ['-start_date']


class AvailabilitySlotCreateView(CreateView):
    model = AvailabilitySlot
    fields = ['asset', 'start_date', 'end_date', 'is_available', 'reserved_by']
    template_name = 'core/availability_slot_form.html'
    success_url = reverse_lazy('core:availability-slot-list')


class AvailabilitySlotDetailView(DetailView):
    model = AvailabilitySlot
    template_name = 'core/availability_slot_detail.html'
    context_object_name = 'slot'


# Deal Views
class DealListView(ListView):
    model = Deal
    template_name = 'core/deal_list.html'
    context_object_name = 'deals'
    paginate_by = 20
    ordering = ['-created_at']


class DealCreateView(CreateView):
    model = Deal
    fields = ['title', 'client', 'manager', 'status', 'expected_amount', 'probability']
    template_name = 'core/deal_form.html'
    success_url = reverse_lazy('core:deal-list')

    def form_valid(self, form):
        messages.success(self.request, 'Сделка успешно создана')
        return super().form_valid(form)


class DealDetailView(DetailView):
    model = Deal
    template_name = 'core/deal_detail.html'
    context_object_name = 'deal'


class DealUpdateView(UpdateView):
    model = Deal
    fields = ['title', 'client', 'manager', 'status', 'expected_amount', 'probability']
    template_name = 'core/deal_form.html'
    success_url = reverse_lazy('core:deal-list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные сделки обновлены')
        return super().form_valid(form)


class DealDeleteView(DeleteView):
    model = Deal
    template_name = 'core/deal_confirm_delete.html'
    success_url = reverse_lazy('core:deal-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Сделка удалена')
        return super().delete(request, *args, **kwargs)


# Contract Views
class ContractListView(ListView):
    model = Contract
    template_name = 'core/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20
    ordering = ['-start_date']


class ContractCreateView(CreateView):
    model = Contract
    fields = ['number', 'client', 'deal', 'start_date', 'end_date', 'total_amount',
              'payment_type', 'signed', 'signed_date']
    template_name = 'core/contract_form.html'
    success_url = reverse_lazy('core:contract-list')

    def form_valid(self, form):
        messages.success(self.request, 'Договор успешно создан')
        return super().form_valid(form)


class ContractDetailView(DetailView):
    model = Contract
    template_name = 'core/contract_detail.html'
    context_object_name = 'contract'


class ContractUpdateView(UpdateView):
    model = Contract
    fields = ['number', 'client', 'deal', 'start_date', 'end_date', 'total_amount',
              'payment_type', 'signed', 'signed_date']
    template_name = 'core/contract_form.html'
    success_url = reverse_lazy('core:contract-list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные договора обновлены')
        return super().form_valid(form)


class ContractAssetDeleteView(DeleteView):
    model = Contract
    template_name = 'core/contract_asset_confirm_delete.html'
    success_url = reverse_lazy('core:contract-list')


# Payment Views
class PaymentListView(ListView):
    model = Payment
    template_name = 'core/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    ordering = ['-date']


class PaymentCreateView(CreateView):
    model = Payment
    fields = ['contract', 'amount', 'date', 'payment_method', 'status',
              'is_confirmed', 'confirmation_date', 'notes', 'transaction_id']
    template_name = 'core/payment_form.html'
    success_url = reverse_lazy('core:payment-list')

    def form_valid(self, form):
        messages.success(self.request, 'Платеж успешно создан')
        return super().form_valid(form)


class PaymentDetailView(DetailView):
    model = Payment
    template_name = 'core/payment_detail.html'
    context_object_name = 'payment'


# Task Views
class DealTaskListView(ListView):
    model = DealTask
    template_name = 'core/deal_task_list.html'
    context_object_name = 'tasks'
    paginate_by = 50
    ordering = ['-due_date']


class DealTaskCreateView(CreateView):
    model = DealTask
    fields = ['deal', 'assigned_to', 'title', 'description', 'is_done',
              'due_date', 'priority']
    template_name = 'core/deal_task_form.html'
    success_url = reverse_lazy('core:task-list')

    def form_valid(self, form):
        messages.success(self.request, 'Задача успешно создана')
        return super().form_valid(form)


class DealTaskDetailView(DetailView):
    model = DealTask
    template_name = 'core/deal_task_detail.html'
    context_object_name = 'task'


class DealTaskUpdateView(UpdateView):
    model = DealTask
    fields = ['deal', 'assigned_to', 'title', 'description', 'is_done',
              'due_date', 'priority', 'completed_at']
    template_name = 'core/deal_task_form.html'
    success_url = reverse_lazy('core:task-list')

    def form_valid(self, form):
        messages.success(self.request, 'Задача обновлена')
        return super().form_valid(form)


class DealTaskDeleteView(DeleteView):
    model = DealTask
    template_name = 'core/deal_task_confirm_delete.html'
    success_url = reverse_lazy('core:task-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Задача удалена')
        return super().delete(request, *args, **kwargs)