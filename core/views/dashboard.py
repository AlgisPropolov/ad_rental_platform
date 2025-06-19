from django.shortcuts import render
from core.services.analytics import get_financial_summary, get_asset_utilization
from core.services.notifications import get_due_soon_tasks


def dashboard_view(request):
    finance = get_financial_summary()
    assets = get_asset_utilization()
    tasks = get_due_soon_tasks()

    context = {
        'finance': finance,
        'assets': assets,
        'tasks': tasks,
    }
    return render(request, 'core/dashboard.html', context)
