from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    RentalPeriod, FinancialReport,
    Dashboard
)
from .resources import RentalPeriodResource

@admin.register(RentalPeriod)
class RentalPeriodAdmin(ImportExportModelAdmin):
    resource_class = RentalPeriodResource
    list_display = ('contract', 'start_date', 'end_date', 'actual_price')
    list_filter = ('contract__asset__asset_type',)
    search_fields = ('contract__number',)

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'period_type', 'period_start', 'period_end')
    actions = ['generate_reports']

    def generate_reports(self, request, queryset):
        for report in queryset:
            report.generate_excel()
            report.generate_word()
        self.message_user(request, "Отчеты успешно сгенерированы")

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_default')
    filter_horizontal = ('allowed_users',)