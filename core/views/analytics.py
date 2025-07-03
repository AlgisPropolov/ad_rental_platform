from django.shortcuts import render
from django.db.models import Sum, Count
from core.models import Payment, Deal, Asset
from django.utils import timezone
from collections import defaultdict
import datetime
import json


def analytics_view(request):
    now = timezone.now()
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if not start_date:
        start_date = now.replace(day=1).date()
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    if not end_date:
        end_date = now.date()
    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Доход по месяцам
    payments = Payment.objects.filter(date__range=(start_date, end_date))
    income_by_month = defaultdict(float)
    for p in payments:
        key = p.date.strftime('%Y-%m')
        income_by_month[key] += float(p.amount)

    # Кол-во сделок по дате
    deals = Deal.objects.filter(start_date__range=(start_date, end_date))
    deals_by_month = defaultdict(int)
    for d in deals:
        key = d.start_date.strftime('%Y-%m')
        deals_by_month[key] += 1

    # Загруженность объектов
    total_assets = Asset.objects.count()
    active_deals = Deal.objects.filter(end_date__gte=now.date())
    used_assets = active_deals.values_list('asset_id', flat=True).distinct().count()
    utilization = round((used_assets / total_assets) * 100, 2) if total_assets else 0

    context = {
        'start': start_date,
        'end': end_date,
        'income_labels': list(income_by_month.keys()),
        'income_values': list(income_by_month.values()),
        'deals_labels': list(deals_by_month.keys()),
        'deals_values': list(deals_by_month.values()),
        'utilization': utilization,
    }

    return render(request, 'core/analytics/index.html', context)
