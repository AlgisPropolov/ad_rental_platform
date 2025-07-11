from .dashboard import DashboardView, dashboard_view
from .analytics import AnalyticsView, analytics_view
from .availability import AvailabilityView, availability_view
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
    ContractDeleteView,
    ContractAssetDeleteView
)
from .payments import (
    PaymentListView,
    PaymentCreateView,
    PaymentDetailView
)
from .tasks import (
    DealTaskListView as TaskListView,
    DealTaskCreateView as TaskCreateView,
    DealTaskDetailView as TaskDetailView,
    DealTaskUpdateView as TaskUpdateView,
    DealTaskDeleteView as TaskDeleteView
)

__all__ = [
    # Dashboard
    'DashboardView', 'AnalyticsView', 'AvailabilityView',
    'dashboard_view', 'analytics_view', 'availability_view',

    # Clients
    'ClientListView', 'ClientCreateView', 'ClientDetailView',
    'ClientUpdateView', 'ClientDeleteView',

    # Assets
    'AssetListView', 'AssetCreateView', 'AssetDetailView',
    'AssetUpdateView', 'AssetDeleteView', 'AssetSlotsView',

    # Deals
    'DealListView', 'DealCreateView', 'DealDetailView',
    'DealUpdateView', 'DealDeleteView',

    # Contracts
    'ContractListView', 'ContractCreateView', 'ContractDetailView',
    'ContractUpdateView', 'ContractDeleteView', 'ContractAssetDeleteView',

    # Payments
    'PaymentListView', 'PaymentCreateView', 'PaymentDetailView',

    # Tasks
    'TaskListView', 'TaskCreateView', 'TaskDetailView',
    'TaskUpdateView', 'TaskDeleteView'
]