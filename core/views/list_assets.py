from django.shortcuts import render
from core.models import Asset

def list_assets_view(request):
    asset_type = request.GET.get('type', '')
    assets = Asset.objects.all()
    if asset_type:
        assets = assets.filter(asset_type=asset_type)
    return render(request, 'core/list_assets.html', {'assets': assets, 'asset_type': asset_type})
