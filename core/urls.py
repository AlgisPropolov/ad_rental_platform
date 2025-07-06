from django.urls import path
from core.views import (
    dashboard_view,
    analytics_view,
    availability_view,
    clients,
    assets,
    deals,
    contracts,
    payments,
    tasks
)

urlpatterns = [
    # Dashboard
    path('', dashboard_view, name='dashboard'),

    # Analytics
    path('analytics/', analytics_view, name='analytics'),

    # Availability
    path('availability/', availability_view, name='availability'),

    # Clients
    path('clients/', clients.ClientListView.as_view(), name='client-list'),
    path('clients/create/', clients.ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', clients.ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/edit/', clients.ClientUpdateView.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', clients.ClientDeleteView.as_view(), name='client-delete'),

    # Assets
    path('assets/', assets.AssetListView.as_view(), name='asset-list'),
    path('assets/create/', assets.AssetCreateView.as_view(), name='asset-create'),
    path('assets/<int:pk>/', assets.AssetDetailView.as_view(), name='asset-detail'),
    path('assets/<int:pk>/edit/', assets.AssetUpdateView.as_view(), name='asset-update'),
    path('assets/<int:pk>/delete/', assets.AssetDeleteView.as_view(), name='asset-delete'),

    # Deals
    path('deals/', deals.DealListView.as_view(), name='deal-list'),
    path('deals/create/', deals.DealCreateView.as_view(), name='deal-create'),
    path('deals/<int:pk>/', deals.DealDetailView.as_view(), name='deal-detail'),
    path('deals/<int:pk>/edit/', deals.DealUpdateView.as_view(), name='deal-update'),
    path('deals/<int:pk>/delete/', deals.DealDeleteView.as_view(), name='deal-delete'),

    # Contracts
    path('contracts/', contracts.ContractListView.as_view(), name='contract-list'),
    path('contracts/create/', contracts.ContractCreateView.as_view(), name='contract-create'),
    path('contracts/<int:pk>/', contracts.ContractDetailView.as_view(), name='contract-detail'),
    path('contracts/<int:pk>/edit/', contracts.ContractUpdateView.as_view(), name='contract-update'),
    path('contract-assets/<int:pk>/delete/',
         contracts.ContractAssetDeleteView.as_view(),
         name='contract-asset-delete'),

    # Payments
    path('payments/', payments.PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', payments.PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', payments.PaymentDetailView.as_view(), name='payment-detail'),

    # Tasks
    path('tasks/', tasks.TaskListView.as_view(), name='task-list'),
    path('tasks/create/', tasks.TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', tasks.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/edit/', tasks.TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', tasks.TaskDeleteView.as_view(), name='task-delete'),
]