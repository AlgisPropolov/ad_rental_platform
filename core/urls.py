from django.urls import path
from django.views.generic import RedirectView
from core.views import (
    dashboard_view,
    analytics_view,
    availability_view,
    # Импортируем view напрямую
    ClientListView,
    ClientCreateView,
    ClientDetailView,
    ClientUpdateView,
    ClientDeleteView,
    AssetListView,
    AssetCreateView,
    AssetDetailView,
    AssetUpdateView,
    AssetDeleteView,
    AssetSlotsView,
    DealListView,
    DealCreateView,
    DealDetailView,
    DealUpdateView,
    DealDeleteView,
    ContractListView,
    ContractCreateView,
    ContractDetailView,
    ContractUpdateView,
    ContractAssetDeleteView,
    PaymentListView,
    PaymentCreateView,
    PaymentDetailView,
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    TaskDeleteView
)

app_name = 'core'

urlpatterns = [
    # Dashboard и перенаправления
    path('', dashboard_view, name='dashboard'),
    path('home/', RedirectView.as_view(pattern_name='core:dashboard', permanent=False)),

    # Аналитика
    path('analytics/', analytics_view, name='analytics'),

    # Доступность
    path('availability/', availability_view, name='availability'),

    # Клиенты
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),

    # Активы
    path('assets/', AssetListView.as_view(), name='asset-list'),
    path('assets/create/', AssetCreateView.as_view(), name='asset-create'),
    path('assets/<int:pk>/', AssetDetailView.as_view(), name='asset-detail'),
    path('assets/<int:pk>/edit/', AssetUpdateView.as_view(), name='asset-update'),
    path('assets/<int:pk>/delete/', AssetDeleteView.as_view(), name='asset-delete'),
    path('assets/<int:asset_id>/slots/', AssetSlotsView.as_view(), name='asset-slots'),

    # Сделки
    path('deals/', DealListView.as_view(), name='deal-list'),
    path('deals/create/', DealCreateView.as_view(), name='deal-create'),
    path('deals/<int:pk>/', DealDetailView.as_view(), name='deal-detail'),
    path('deals/<int:pk>/edit/', DealUpdateView.as_view(), name='deal-update'),
    path('deals/<int:pk>/delete/', DealDeleteView.as_view(), name='deal-delete'),

    # Контракты
    path('contracts/', ContractListView.as_view(), name='contract-list'),
    path('contracts/create/', ContractCreateView.as_view(), name='contract-create'),
    path('contracts/<int:pk>/', ContractDetailView.as_view(), name='contract-detail'),
    path('contracts/<int:pk>/edit/', ContractUpdateView.as_view(), name='contract-update'),
    path('contract-assets/<int:pk>/delete/', ContractAssetDeleteView.as_view(), name='contract-asset-delete'),

    # Платежи
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),

    # Задачи
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
]