from django.contrib import admin
from django.urls import path, include
from core.views import availability_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('availability/', availability_view, name='availability'),
    path('', include('core.urls')),  # если у вас есть другие маршруты в core/urls.py
    # другие маршруты проекта
]