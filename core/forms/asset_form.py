from django import forms
from core.models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'location', 'is_active']
        labels = {
            'name': 'Название объекта',
            'asset_type': 'Тип объекта',
            'location': 'Местоположение',
            'is_active': 'Активен',
        }
