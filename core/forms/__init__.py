from .client import ClientForm
from .deal import DealForm
from .contract import ContractForm, ContractAssetForm
from .asset import AssetForm

# Опциональные формы (если файлы существуют)
try:
    from .payment import PaymentForm
except ImportError:
    PaymentForm = None

try:
    from .task import TaskForm
except ImportError:
    TaskForm = None

__all__ = [
    'ClientForm',
    'ClientForm',
    'DealForm',
    'ContractForm',
    'ContractAssetForm',
    'AssetForm',
] + (['PaymentForm'] if PaymentForm is not None else []) + (['TaskForm'] if TaskForm is not None else [])