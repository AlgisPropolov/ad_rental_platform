from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django import forms
from core.models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

def create_asset_view(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset-list')
    else:
        form = AssetForm()
    return render(request, 'core/assets/create.html', {'form': form})

def list_assets_view(request):
    assets = Asset.objects.all().order_by('name')
    return render(request, 'core/assets/list.html', {'assets': assets})

def edit_asset_view(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('asset-list')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'core/assets/edit.html', {'form': form})

def delete_asset_view(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        return redirect('asset-list')
    return render(request, 'core/assets/delete.html', {'asset': asset})