from django.shortcuts import render, redirect
from django import forms
from core.models import Asset

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
