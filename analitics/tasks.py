from celery import shared_task
from .models import FinancialReport, Dashboard
from django.utils import timezone


@shared_task
def generate_reports():
    """Генерация отчетов по расписанию"""
    today = timezone.now().date()
    reports = FinancialReport.objects.filter(
        period_end__lte=today,
        excel_file__isnull=True
    )

    for report in reports:
        report.generate_excel()
        report.generate_word()


@shared_task
def update_dashboards():
    """Обновление данных для дашбордов"""
    dashboards = Dashboard.objects.filter(is_active=True)
    for dashboard in dashboards:
        # Логика обновления данных
        dashboard.save()