from django.views.generic import TemplateView
from django.db.models import Sum
from ..models import Payment, Contract, Asset, AvailabilitySlot, DealTask
from django.utils import timezone


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Финансовая аналитика
        context['finance'] = {
            'total_income': Payment.objects.filter(is_confirmed=True).aggregate(Sum('amount'))['amount__sum'] or 0,
            'unpaid_amount': Contract.objects.filter(is_active=True).aggregate(Sum('total_amount'))[
                                 'total_amount__sum'] or 0
        }

        # Статистика по активам
        context['assets'] = {
            'total_assets': Asset.objects.count(),
            'used_assets': AvailabilitySlot.objects.filter(is_available=False).count(),
            'available_assets': AvailabilitySlot.objects.filter(is_available=True).count()
        }

        # Ближайшие задачи
        context['tasks'] = DealTask.objects.filter(
            is_done=False,
            due_date__lte=timezone.now() + timezone.timedelta(days=3)
        ).order_by('due_date')[:5]

        return context


def dashboard_view(request):
    # Резервное функциональное представление
    return DashboardView.as_view()(request)