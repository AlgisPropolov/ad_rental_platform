# core/views/contracts.py
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Contract
from core.forms import ContractForm

def list_contracts_view(request):
    contracts = Contract.objects.select_related('client', 'asset').all()
    return render(request, 'core/contracts/list.html', {'contracts': contracts})

def create_contract_view(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_contracts')
    else:
        form = ContractForm()
    return render(request, 'core/contracts/create.html', {'form': form})
