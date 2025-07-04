from django.shortcuts import render
from django.utils import timezone
from ..models import Deal, Contract, Payment


def analytics_view(request):
    # Получаем даты для фильтрации (последние 30 дней)
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=30)

    # Исправленный запрос - используем created_at вместо start_date
    deals = Deal.objects.filter(created_at__range=(start_date, end_date))
    contracts = Contract.objects.filter(created_at__range=(start_date, end_date))
    payments = Payment.objects.filter(date__range=(start_date, end_date))

    context = {
        'deals': deals,
        'contracts': contracts,
        'payments': payments,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'core/analytics/dashboard.html', context)