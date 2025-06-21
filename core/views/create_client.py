from django.shortcuts import render, redirect
from django import forms
from core.models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'inn', 'contact_person', 'phone', 'email']

def create_client_view(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ClientForm()
    return render(request, 'core/create_client.html', {'form': form})
