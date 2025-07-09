from .tasks import (
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    TaskDeleteView
)
from .clients import (
    ClientListView,
    ClientCreateView,
    ClientDetailView,
    ClientUpdateView,
    ClientDeleteView
)
from .assets import (
    AssetListView,
    AssetCreateView,
    AssetDetailView,
    AssetUpdateView,
    AssetDeleteView,
    AssetSlotsView
)
from .deals import (
    DealListView,
    DealCreateView,
    DealDetailView,
    DealUpdateView,
    DealDeleteView
)
from .contracts import (
    ContractListView,
    ContractCreateView,
    ContractDetailView,
    ContractUpdateView,
    ContractAssetDeleteView
)
from .payments import (
    PaymentListView,
    PaymentCreateView,
    PaymentDetailView
)
from .dashboard import dashboard_view
from .analytics import analytics_view
from .availability import availability_view

# Экспортируем все View напрямую (рекомендуемый способ)
__all__ = [
    # Основные view
    'dashboard_view',
    'analytics_view',
    'availability_view',

    # Clients
    'ClientListView',
    'ClientCreateView',
    'ClientDetailView',
    'ClientUpdateView',
    'ClientDeleteView',

    # Assets
    'AssetListView',
    'AssetCreateView',
    'AssetDetailView',
    'AssetUpdateView',
    'AssetDeleteView',
    'AssetSlotsView',

    # Deals
    'DealListView',
    'DealCreateView',
    'DealDetailView',
    'DealUpdateView',
    'DealDeleteView',

    # Contracts
    'ContractListView',
    'ContractCreateView',
    'ContractDetailView',
    'ContractUpdateView',
    'ContractAssetDeleteView',

    # Payments
    'PaymentListView',
    'PaymentCreateView',
    'PaymentDetailView',

    # Tasks
    'TaskListView',
    'TaskCreateView',
    'TaskDetailView',
    'TaskUpdateView',
    'TaskDeleteView'
]