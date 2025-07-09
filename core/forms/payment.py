from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from ..models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['contract', 'amount', 'date', 'payment_method', 'status', 'is_confirmed', 'notes',
                  'confirmation_date', 'transaction_id']
        labels = {
            'contract': _('Договор'),
            'amount': _('Сумма'),
            'date': _('Дата платежа'),  # Изменено с payment_date на date
            'payment_method': _('Способ оплаты'),
            'status': _('Статус'),
            'is_confirmed': _('Подтвержден'),
            'confirmation_date': _('Дата подтверждения'),
            'notes': _('Примечания'),
            'transaction_id': _('ID транзакции')
        }
        widgets = {
            'date': forms.DateInput(attrs={  # Изменено с payment_date на date
                'type': 'date',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_confirmed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'confirmation_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'contract': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError(_('Сумма должна быть положительной'))
        return amount

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')

        if date and date > timezone.now().date():
            raise forms.ValidationError({
                'date': _('Дата платежа не может быть в будущем')
            })

        return cleaned_data