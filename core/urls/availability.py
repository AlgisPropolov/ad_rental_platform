from django.urls import path
from core.views.availability import AvailabilityView, availability_view

urlpatterns = [
    path('', AvailabilityView.as_view(), name='availability'),
    path('api/', availability_view, name='availability-api'),
]