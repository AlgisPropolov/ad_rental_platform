from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import availability_view  # Перенесли импорт сюда

urlpatterns = [
    # Административная панель
    path('admin/', admin.site.urls),

    # API endpoints (все API-маршруты теперь в core.api.urls)
    path('api/', include('core.api.urls')),

    # Основные views
    path('availability/', availability_view, name='availability'),

    # Подключение URL из приложения core
    path('', include(('core.urls', 'core'), namespace='core')),

    # Подключение URL из приложения users
    path('accounts/', include(('users.urls', 'users'), namespace='users')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Отладочные URL
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns