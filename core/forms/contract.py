from django import forms
from django.utils.translation import gettext_lazy as _
from core.models import Contract, ContractAsset


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'number',
            'client',
            'deal',
            'start_date',
            'end_date',
            'total_amount',
            'payment_type',
            'signed',
            'signed_date',
            'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'signed_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'number': _('Номер договора'),
            'client': _('Клиент'),
            'deal': _('Сделка'),
            'start_date': _('Дата начала'),
            'end_date': _('Дата окончания'),
            'total_amount': _('Общая сумма'),
            'payment_type': _('Тип оплаты'),
            'signed': _('Подписан'),
            'signed_date': _('Дата подписания'),
            'is_active': _('Действующий'),
        }


class ContractAssetForm(forms.ModelForm):
    class Meta:
        model = ContractAsset
        fields = [
            'contract',
            'asset',
            'slot',
            'price',
            'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'contract': _('Договор'),
            'asset': _('Актив'),
            'slot': _('Слот доступности'),
            'price': _('Цена'),
            'notes': _('Примечания'),
        }