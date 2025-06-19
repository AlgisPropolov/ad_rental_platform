from datetime import date
from django.db.models import Sum, Count
from core.models import Contract, Payment, Asset

def get_financial_summary():
    total_income = Payment.objects.filter(is_confirmed=True).aggregate(Sum('amount'))['amount__sum'] or 0
    unpaid = Payment.objects.filter(is_confirmed=False).aggregate(Sum('amount'))['amount__sum'] or 0
    return {
        'total_income': total_income,
        'unpaid_amount': unpaid
    }

def get_asset_utilization():
    assets = Asset.objects.count()
    used = Contract.objects.filter(end_date__gte=date.today()).count()
    return {
        'total_assets': assets,
        'used_assets': used,
        'available_assets': assets - used
    }
