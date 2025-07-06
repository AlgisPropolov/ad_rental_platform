from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from core.models import Contract, ContractAsset
from core.forms import ContractForm, ContractAssetForm


class ContractListView(ListView):
    model = Contract
    template_name = 'contracts/list.html'
    context_object_name = 'contracts'
    ordering = ['-created_at']
    paginate_by = 20


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
            'asset_form': asset_form
        })


class ContractUpdateView(View):
    template_name = 'contracts/update.html'

    def get(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        form = ContractForm(instance=contract)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, 'Договор успешно обновлен')
            return redirect('contract-detail', pk=contract.pk)
        return render(request, self.template_name, {'form': form})


class ContractAssetDeleteView(View):
    def post(self, request, pk):
        asset = get_object_or_404(ContractAsset, pk=pk)
        contract = asset.contract
        asset.delete()

        # Обновляем сумму договора
        contract.total_amount = sum(
            ca.price for ca in contract.contract_assets.all()
        )
        contract.save()

        messages.success(request, 'Актив удален из договора')
        return redirect('contract-detail', pk=contract.pk)


# Альтернативные функциональные представления (если нужны)
def list_contracts_view(request):
    contracts = Contract.objects.select_related('client', 'deal').order_by('-created_at')
    return render(request, 'contracts/list.html', {'contracts': contracts})


def create_contract_view(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            messages.success(request, 'Договор успешно создан')
            return redirect('contract-detail', pk=contract.pk)
    else:
        form = ContractForm()
    return render(request, 'contracts/create.html', {'form': form})