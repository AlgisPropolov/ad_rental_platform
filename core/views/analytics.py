from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta
from ..models import Deal, Contract, Payment, Client, Asset


def get_deals_metrics():
    """Возвращает метрики по сделкам"""
    return {
        'total': Deal.objects.count(),
        'active': Deal.objects.filter(status='in_progress').count(),
        'completed': Deal.objects.filter(status='won').count(),
        'in_approval': Deal.objects.filter(status='approval').count()
    }


def get_financial_metrics():
    """Возвращает финансовые метрики"""
    return {
        'income': Payment.objects.filter(is_confirmed=True).aggregate(total=Sum('amount'))['total'] or 0,
        'expected': Contract.objects.filter(is_active=True).aggregate(total=Sum('total_amount'))['total'] or 0,
        'debt': Contract.objects.filter(
            is_active=True,
            payments__is_confirmed=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0
    }


def get_deals_timeline(date_from):
    """Возвращает данные для графика сделок по времени"""
    timeline = (
        Deal.objects
        .filter(created_at__date__gte=date_from)
        .extra({'day': "date(created_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    return {
        'labels': [str(item['day']) for item in timeline],
        'data': [item['count'] for item in timeline]
    }


def get_assets_distribution():
    """Распределение активов по типам с исправленным расчетом доходности"""
    distribution = (
        Contract.objects
        .values('assets__asset_type')  # Группировка по типу актива
        .annotate(
            count=Count('id', distinct=True),  # Количество контрактов
            total=Sum('total_amount')  # Сумма по полю total_amount вместо price
        )
        .order_by('-total')
    )

    return {
        'labels': [
            dict(Asset.AssetType.choices).get(item['assets__asset_type'], 'Другое')
            for item in distribution
        ],
        'data': [item['count'] for item in distribution],
        'revenue': [item['total'] for item in distribution]
    }


def get_top_clients(limit=5):
    """Топ клиентов по объему контрактов"""
    return (
        Client.objects
        .filter(is_active=True)  # Добавлено фильтрация по активным клиентам
        .annotate(
            contract_count=Count('contracts', distinct=True),
            total_amount=Sum('contracts__total_amount')
        )
        .filter(total_amount__gt=0)  # Только клиенты с контрактами
        .order_by('-total_amount')[:limit]
        .values('name', 'contact_person', 'contract_count', 'total_amount')
    )


class AnalyticsPeriod:
    """Класс для работы с периодами аналитики"""
    PERIODS = {
        'week': ('неделю', 7),
        'month': ('месяц', 30),
        'quarter': ('квартал', 90),
        'year': ('год', 365)
    }

    def __init__(self, period_str='month'):
        period = self.PERIODS.get(period_str, self.PERIODS['month'])
        self.label = period[0]
        self.days = period[1]
        self.date_from = timezone.now().date() - timedelta(days=self.days)
        self.date_to = timezone.now().date()


class AnalyticsView(TemplateView):
    """Класс-представление для аналитики"""
    template_name = 'core/analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = AnalyticsPeriod(self.request.GET.get('period', 'month'))

        context.update({
            'deals': get_deals_metrics(),
            'finance': get_financial_metrics(),
            'timeline': get_deals_timeline(period.date_from),
            'distribution': get_assets_distribution(),
            'period': {
                'current': self.request.GET.get('period', 'month'),
                'label': period.label,
                'date_from': period.date_from,
                'date_to': period.date_to
            },
            'top_clients': list(get_top_clients()),
        })
        return context


def analytics_view(request):
    """Функциональное представление аналитики"""
    period = AnalyticsPeriod(request.GET.get('period', 'month'))

    context = {
        'deals': get_deals_metrics(),
        'finance': get_financial_metrics(),
        'timeline': get_deals_timeline(period.date_from),
        'distribution': get_assets_distribution(),
        'period': {
            'current': request.GET.get('period', 'month'),
            'label': period.label,
            'date_from': period.date_from,
            'date_to': period.date_to
        },
        'top_clients': list(get_top_clients()),
    }
    return render(request, 'core/analytics/dashboard.html', context)