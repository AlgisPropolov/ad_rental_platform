# core/views/payments.py
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Payment, Contract
from django import forms


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['contract', 'date', 'amount', 'is_confirmed']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


def list_payments_view(request):
    payments = Payment.objects.select_related('contract').order_by('-date')
    return render(request, 'core/payments/list.html', {'payments': payments})


def create_payment_view(request):
    form = PaymentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('list_payments')
    return render(request, 'core/payments/create.html', {'form': form})
