from django.urls import path
from .views.dashboard import dashboard_view
from .views.availability import availability_view
from .views.create_client import create_client_view
from .views.create_asset import create_asset_view
from .views.deals import list_deals_view, create_deal_view, edit_deal_view, delete_deal_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('availability/', availability_view, name='availability'),
    path('clients/create/', create_client_view, name='create_client'),
    path('assets/create/', create_asset_view, name='create_asset'),
    path('deals/', list_deals_view, name='list_deals'),
    path('deals/create/', create_deal_view, name='create_deal'),
    path('deals/<int:pk>/edit/', edit_deal_view, name='edit_deal'),
    path('deals/<int:pk>/delete/', delete_deal_view, name='delete_deal'),
]
