from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.api.views import asset_slots
from core.views import availability_view

urlpatterns = [
    # Административная панель
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/assets/<int:asset_id>/slots/', asset_slots, name='asset-slots'),

    # Основные views
    path('availability/', availability_view, name='availability'),

    # Подключение URL из приложения core (с явным указанием app_name)
    path('', include(('core.urls', 'core'), namespace='core')),

    # Подключение URL из приложения users (с явным указанием app_name)
    path('accounts/', include(('users.urls', 'users'), namespace='users')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Добавляем отладочные URL в режиме разработки
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns