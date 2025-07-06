from .client import ClientForm
from .deal import DealForm
from .contract import ContractForm, ContractAssetForm
from .asset import AssetForm

# Условный импорт для необязательных форм
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
    'DealForm',
    'ContractForm',
    'ContractAssetForm',
    'AssetForm'
]

# Добавляем только если формы существуют
if PaymentForm is not None:
    __all__.append('PaymentForm')

if TaskForm is not None:
    __all__.append('TaskForm')