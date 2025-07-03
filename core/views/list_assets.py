from django.shortcuts import render
from core.models import Asset
from django import forms

class AssetFilterForm(forms.Form):
    search = forms.CharField(required=False, label='Поиск', widget=forms.TextInput(attrs={'placeholder': 'Название или локация'}))
    asset_type = forms.ChoiceField(required=False,
        choices=[('', 'Все'), ('bus','Автобус'),('stop','Остановка'),('screen','Экран')]
    )

def list_assets_view(request):
    form = AssetFilterForm(request.GET or None)
    qs = Asset.objects.all().order_by('name')
    if form.is_valid():
        s = form.cleaned_data['search']
        if s:
            qs = qs.filter(name__icontains=s) | qs.filter(location__icontains=s)
        t = form.cleaned_data['asset_type']
        if t:
            qs = qs.filter(asset_type=t)
    return render(request, 'core/assets/list.html', {'assets': qs, 'form': form})
