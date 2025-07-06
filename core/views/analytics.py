from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta
from ..models import Deal, Contract, Payment, Client


def analytics_view(request):
    # Определяем период для аналитики
    period = request.GET.get('period', 'month')

    if period == 'week':
        date_from = timezone.now().date() - timedelta(days=7)
        period_label = "неделю"
    elif period == 'quarter':
        date_from = timezone.now().date() - timedelta(days=90)
        period_label = "квартал"
    elif period == 'year':
        date_from = timezone.now().date() - timedelta(days=365)
        period_label = "год"
    else:  # month по умолчанию
        date_from = timezone.now().date() - timedelta(days=30)
        period_label = "месяц"

    # Основные метрики
    deals_count = Deal.objects.count()
    active_deals_count = Deal.objects.filter(status='in_progress').count()
    completed_deals_count = Deal.objects.filter(status='won').count()

    # Финансовые показатели
    total_income = Payment.objects.filter(
        is_confirmed=True
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Динамика сделок по дням
    deals_timeline = (
        Deal.objects
        .filter(created_at__date__gte=date_from)
        .extra({'day': "date(created_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Распределение по типам активов
    deal_types = (
        Contract.objects
        .values('asset__asset_type')
        .annotate(count=Count('id'), total=Sum('price'))
        .order_by('-count')
    )

    # Подготовка данных для графиков
    deals_timeline_labels = [str(item['day']) for item in deals_timeline]
    deals_timeline_data = [item['count'] for item in deals_timeline]

    deal_types_labels = [dict(Asset.AssetType.choices).get(item['asset__asset_type'], 'Другое')
                         for item in deal_types]
    deal_types_data = [item['count'] for item in deal_types]

    context = {
        # Основные метрики
        'deals_count': deals_count,
        'active_deals_count': active_deals_count,
        'completed_deals_count': completed_deals_count,
        'total_income': total_income,

        # Данные для графиков
        'deals_timeline_labels': deals_timeline_labels,
        'deals_timeline_data': deals_timeline_data,
        'deal_types_labels': deal_types_labels,
        'deal_types_data': deal_types_data,

        # Фильтры
        'period': period,
        'period_label': period_label,
        'date_from': date_from,
        'date_to': timezone.now().date(),

        # Дополнительные данные
        'top_clients': Client.objects.annotate(
            deal_count=Count('deals'),
            total_contracts=Sum('contracts__price')
        ).order_by('-total_contracts')[:5],
    }

    return render(request, 'core/analytics/dashboard.html', context)