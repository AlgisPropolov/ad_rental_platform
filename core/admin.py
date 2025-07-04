from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client, Asset, Contract, AvailabilitySlot, Payment, Deal, DealTask

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'contact_person', 'phone', 'email', 'get_created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'inn', 'contact_person', 'phone')
    readonly_fields = ('get_created_at', 'get_updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'inn')
        }),
        ('Контактная информация', {
            'fields': ('contact_person', 'phone', 'email')
        }),
        ('Системная информация', {
            'fields': ('get_created_at', 'get_updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Дата создания'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Дата обновления'

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'location', 'is_active', 'get_created_at')
    list_filter = ('asset_type', 'is_active')
    search_fields = ('name', 'location')
    list_editable = ('is_active',)
    readonly_fields = ('get_created_at', 'get_updated_at')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Дата создания'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Дата обновления'

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('asset', 'start_date', 'end_date', 'is_available', 'get_created_at')
    list_filter = ('is_available', 'start_date', 'end_date')
    search_fields = ('asset__name',)
    readonly_fields = ('get_created_at', 'get_updated_at')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Дата создания'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Дата обновления'

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'get_created_at', 'get_updated_at', 'get_closed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'client__name')
    readonly_fields = ('get_created_at', 'get_updated_at', 'get_closed_at')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Дата создания'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Дата обновления'

    def get_closed_at(self, obj):
        return obj.closed_at
    get_closed_at.short_description = 'Дата закрытия'

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'asset', 'start_date', 'end_date', 'price', 'signed', 'get_created_at')
    list_filter = ('signed', 'start_date', 'end_date')
    search_fields = ('number', 'client__name', 'asset__name')
    readonly_fields = ('get_created_at', 'get_updated_at')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Дата создания'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Дата обновления'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'date', 'amount', 'is_confirmed', 'get_created_at')
    list_filter = ('is_confirmed', 'date')
    search_fields = ('contract__number', 'contract__client__name')
    readonly_fields = ('get_created_at', 'get_updated_at')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Дата создания'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Дата обновления'

@admin.register(DealTask)
class DealTaskAdmin(admin.ModelAdmin):
    list_display = ('deal', 'description', 'is_done', 'due_date', 'get_priority_display', 'get_created_at')
    list_filter = ('is_done', 'due_date')
    list_editable = ('is_done',)
    search_fields = ('deal__title', 'description')
    readonly_fields = ('get_created_at', 'get_updated_at')

    def get_priority_display(self, obj):
        return obj.get_priority_display()
    get_priority_display.short_description = 'Приоритет'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Дата создания'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Дата обновления'