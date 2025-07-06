from django.contrib import admin
from django.urls import path, include
from core.api.views import asset_slots
from core.views import availability_view

urlpatterns = [
    # Админ-панель
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/assets/<int:asset_id>/slots/', asset_slots, name='asset-slots'),

    # Основные views
    path('availability/', availability_view, name='availability'),

    # Подключение всех URL из приложения core
    path('', include('core.urls')),

    # Другие маршруты проекта можно добавить здесь
]