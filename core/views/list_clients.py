from django.shortcuts import render
from core.models import Client
from django import forms

class ClientFilterForm(forms.Form):
    search = forms.CharField(required=False, label='Поиск', widget=forms.TextInput(attrs={'placeholder': 'Имя или ИНН'}))

def list_clients_view(request):
    form = ClientFilterForm(request.GET or None)
    qs = Client.objects.all().order_by('name')
    if form.is_valid():
        s = form.cleaned_data['search']
        if s:
            qs = qs.filter(name__icontains=s) | qs.filter(inn__icontains=s)
    return render(request, 'core/clients/list.html', {'clients': qs, 'form': form})
