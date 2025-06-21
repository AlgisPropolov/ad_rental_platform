from django.shortcuts import render, redirect
from core.models import Client, Asset
from django import forms

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

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'location', 'is_active']

def create_asset_view(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AssetForm()
    return render(request, 'core/create_asset.html', {'form': form})
