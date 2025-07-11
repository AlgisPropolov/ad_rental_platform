from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetViewSet,
    ContractViewSet,
    asset_slots  # Добавляем импорт
)

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'contracts', ContractViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Добавляем кастомный маршрут для слотов
    path('assets/<int:asset_id>/slots/', asset_slots, name='asset-slots'),
]