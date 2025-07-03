# ✅ core/forms/contracts.py
from django import forms
from core.models import Contract

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['client', 'asset', 'start_date', 'end_date', 'price', 'signed']
