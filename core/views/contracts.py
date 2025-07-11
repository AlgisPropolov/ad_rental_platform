from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum, Prefetch
from core.models import Contract, ContractAsset, Payment
from core.forms import ContractForm, ContractAssetForm


class ContractBaseView:
    """Базовый класс для представлений договоров"""
    model = Contract
    context_object_name = 'contract'


class ContractListView(ContractBaseView, ListView):
    template_name = 'contracts/list.html'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'client', 'deal'
        ).prefetch_related(
            Prefetch('contract_assets', queryset=ContractAsset.objects.select_related('asset')),
            Prefetch('payments', queryset=Payment.objects.only('amount', 'date'))
        ).annotate(
            paid_amount=Sum('payments__amount')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_contracts'] = self.get_queryset().count()
        return context


class ContractCreateView(ContractBaseView, CreateView):
    form_class = ContractForm
    template_name = 'contracts/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Договор №{self.object.number} успешно создан')
        return response

    def get_success_url(self):
        return reverse_lazy('contract-detail', kwargs={'pk': self.object.pk})


class ContractDetailView(ContractBaseView, DetailView):
    template_name = 'contracts/detail.html'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'client', 'deal'
        ).prefetch_related(
            Prefetch('contract_assets', queryset=ContractAsset.objects.select_related('asset', 'slot')),
            Prefetch('payments', queryset=Payment.objects.order_by('-date'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract = self.object
        context.update({
            'asset_form': ContractAssetForm(contract=contract),
            'paid_amount': contract.payments.aggregate(total=Sum('amount'))['total'] or 0,
            'balance': contract.total_amount - (contract.payments.aggregate(total=Sum('amount'))['total'] or 0)
        })
        return context


class ContractUpdateView(ContractBaseView, UpdateView):
    form_class = ContractForm
    template_name = 'contracts/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Договор №{self.object.number} успешно обновлен')
        return response

    def get_success_url(self):
        return reverse_lazy('contract-detail', kwargs={'pk': self.object.pk})


class ContractDeleteView(ContractBaseView, DeleteView):
    template_name = 'contracts/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        contract = self.get_object()
        if contract.payments.exists():
            messages.error(
                request,
                'Нельзя удалить договор с привязанными платежами'
            )
            return redirect('contract-detail', pk=contract.pk)

        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Договор №{contract.number} успешно удален')
        return response

    def get_success_url(self):
        return reverse_lazy('contract-list')


class ContractAssetDeleteView(DeleteView):
    model = ContractAsset
    template_name = 'contracts/confirm_asset_delete.html'
    context_object_name = 'contract_asset'

    def get_success_url(self):
        contract_id = self.object.contract_id
        messages.success(self.request, 'Актив успешно удален из договора')
        return reverse_lazy('contract-detail', kwargs={'pk': contract_id})

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        contract = self.object.contract
        contract.total_amount = contract.contract_assets.aggregate(
            total=Sum('price')
        )['total'] or 0
        contract.save()
        return response