from django.urls import path
from core.views.dashboard import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
]
