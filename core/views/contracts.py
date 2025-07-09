from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum
from core.models import Contract, ContractAsset, Asset, AvailabilitySlot
from core.forms import ContractForm, ContractAssetForm


class ContractListView(ListView):
    model = Contract
    template_name = 'contracts/list.html'
    context_object_name = 'contracts'
    ordering = ['-created_at']
    paginate_by = 20
    queryset = Contract.objects.select_related('client', 'deal').prefetch_related('contract_assets')


class ContractCreateView(View):
    template_name = 'contracts/create.html'

    def get(self, request):
        form = ContractForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            messages.success(request, 'Договор успешно создан')
            return redirect('contract-detail', pk=contract.pk)
        messages.error(request, 'Исправьте ошибки в форме')
        return render(request, self.template_name, {'form': form})


class ContractDetailView(View):
    template_name = 'contracts/detail.html'

    def get(self, request, pk):
        contract = get_object_or_404(
            Contract.objects.select_related('client', 'deal'),
            pk=pk
        )
        assets = contract.contract_assets.select_related('asset', 'slot')
        asset_form = ContractAssetForm(contract=contract)

        return render(request, self.template_name, {
            'contract': contract,
            'assets': assets,
            'asset_form': asset_form,
            'total_amount': assets.aggregate(total=Sum('price'))['total'] or 0
        })


class ContractUpdateView(View):
    template_name = 'contracts/update.html'

    def get(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        form = ContractForm(instance=contract)
        return render(request, self.template_name, {'form': form, 'contract': contract})

    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, 'Договор успешно обновлен')
            return redirect('contract-detail', pk=contract.pk)
        messages.error(request, 'Исправьте ошибки в форме')
        return render(request, self.template_name, {'form': form, 'contract': contract})


class ContractAssetDeleteView(View):
    def post(self, request, pk):
        asset = get_object_or_404(
            ContractAsset.objects.select_related('contract'),
            pk=pk
        )
        contract = asset.contract
        asset.delete()

        # Обновляем сумму договора через агрегацию
        contract.total_amount = contract.contract_assets.aggregate(
            total=Sum('price')
        )['total'] or 0
        contract.save()

        messages.success(request, 'Актив успешно удален из договора')
        return redirect('contract-detail', pk=contract.pk)


# Альтернативные функциональные представления (опционально)
def list_contracts_view(request):
    contracts = Contract.objects.select_related('client', 'deal').order_by('-created_at')
    return render(request, 'contracts/list.html', {
        'contracts': contracts,
        'total_contracts': contracts.count()
    })


def create_contract_view(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            messages.success(request, 'Договор успешно создан')
            return redirect('contract-detail', pk=contract.pk)
        messages.error(request, 'Ошибка при создании договора')
    else:
        form = ContractForm()

    return render(request, 'contracts/create.html', {'form': form})