from django.urls import path
from core.views.dashboard import dashboard_view
from core.views.availability import availability_view
from core.views.create_client import create_client_view
from core.views.create_asset import create_asset_view
from core.views.analytics import analytics_view
from core.views.deals import list_deals_view, create_deal_view, edit_deal_view, delete_deal_view
from core.views.contracts import list_contracts_view, create_contract_view
from core.views.payments import list_payments_view, create_payment_view
from core.views.deal_tasks import list_tasks_view, create_task_view
from core.views.list_clients import list_clients_view
from core.views.list_assets import list_assets_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('analytics/', analytics_view, name='analytics'),
    path('availability/', availability_view, name='availability'),
    path('clients/create/', create_client_view, name='create_client'),
    path('clients/', list_clients_view, name='list_clients'),
    path('assets/create/', create_asset_view, name='create_asset'),
    path('assets/', list_assets_view, name='list_assets'),
    path('deals/', list_deals_view, name='list_deals'),
    path('deals/create/', create_deal_view, name='create_deal'),
    path('deals/<int:pk>/edit/', edit_deal_view, name='edit_deal'),
    path('deals/<int:pk>/delete/', delete_deal_view, name='delete_deal'),
    path('contracts/', list_contracts_view, name='list_contracts'),
    path('contracts/create/', create_contract_view, name='create_contract'),
    path('payments/', list_payments_view, name='list_payments'),
    path('payments/create/', create_payment_view, name='create_payment'),
    path('tasks/', list_tasks_view, name='list_tasks'),
    path('tasks/create/', create_task_view, name='create_task'),
]
