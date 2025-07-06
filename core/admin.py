from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    Client, Asset, Contract, 
    AvailabilitySlot, Payment, 
    Deal, DealTask, ContractAsset
)


class BaseAdmin(admin.ModelAdmin):
    """Базовый класс для админ-панели с общими настройками"""
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = True
    save_on_top = True


@admin.register(Client)
class ClientAdmin(BaseAdmin):
    list_display = (
        'name', 'inn', 'contact_person', 
        'phone', 'email', 'is_vip', 
        'created_at', 'deals_link'
    )
    list_filter = ('is_vip', 'created_at')
    search_fields = ('name', 'inn', 'contact_person', 'phone')
    list_editable = ('is_vip',)
    fieldsets = (
        (None, {
            'fields': ('name', 'inn', 'is_vip')
        }),
        (_('Контактная информация'), {
            'fields': ('contact_person', 'phone', 'email')
        }),
        (_('Системная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def deals_link(self, obj):
        count = obj.deals.count()
        url = reverse('admin:core_deal_changelist') + f'?client__id__exact={obj.id}'
        return format_html('<a href="{}">{} сделок</a>', url, count)
    deals_link.short_description = _('Сделки')


@admin.register(Asset)
class AssetAdmin(BaseAdmin):
    list_display = (
        'name', 'asset_type', 'zone', 
        'location', 'daily_rate', 'is_active',
        'contracts_link'
    )
    list_filter = ('asset_type', 'zone', 'is_active')
    search_fields = ('name', 'location')
    list_editable = ('is_active', 'daily_rate')
    fieldsets = (
        (None, {
            'fields': ('name', 'asset_type', 'zone', 'location')
        }),
        (_('Финансы'), {
            'fields': ('daily_rate', 'is_active')
        }),
        (_('Дополнительно'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Системная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def contracts_link(self, obj):
        count = obj.contracts.count()
        url = reverse('admin:core_contract_changelist') + f'?asset__id__exact={obj.id}'
        return format_html('<a href="{}">{} договоров</a>', url, count)
    contracts_link.short_description = _('Договоры')


class ContractAssetInline(admin.TabularInline):
    model = ContractAsset
    extra = 1
    fields = ('asset', 'slot', 'price', 'notes')
    raw_id_fields = ('asset', 'slot')


@admin.register(Contract)
class ContractAdmin(BaseAdmin):
    list_display = (
        'number', 'client_link', 'start_date', 
        'end_date', 'total_amount', 'payment_type',
        'signed', 'is_active', 'payments_link'
    )
    list_filter = ('signed', 'is_active', 'payment_type', 'start_date')
    search_fields = ('number', 'client__name')
    list_editable = ('is_active', 'signed')
    inlines = (ContractAssetInline,)
    fieldsets = (
        (None, {
            'fields': ('number', 'client', 'deal')
        }),
        (_('Период действия'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Финансы'), {
            'fields': ('total_amount', 'payment_type')
        }),
        (_('Статус'), {
            'fields': ('signed', 'signed_date', 'is_active')
        }),
        (_('Системная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def client_link(self, obj):
        url = reverse('admin:core_client_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client)
    client_link.short_description = _('Клиент')

    def payments_link(self, obj):
        count = obj.payments.count()
        url = reverse('admin:core_payment_changelist') + f'?contract__id__exact={obj.id}'
        return format_html('<a href="{}">{} платежей</a>', url, count)
    payments_link.short_description = _('Платежи')


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(BaseAdmin):
    list_display = (
        'asset', 'start_date', 'end_date', 
        'is_available', 'reserved_by_link',
        'duration_days'
    )
    list_filter = ('is_available', 'asset__asset_type', 'start_date')
    search_fields = ('asset__name',)
    raw_id_fields = ('reserved_by',)
    readonly_fields = ('duration_days',)

    def reserved_by_link(self, obj):
        if not obj.reserved_by:
            return "-"
        url = reverse('admin:core_contract_change', args=[obj.reserved_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.reserved_by)
    reserved_by_link.short_description = _('Закреплен за')

    def duration_days(self, obj):
        return (obj.end_date - obj.start_date).days
    duration_days.short_description = _('Дней')


@admin.register(Deal)
class DealAdmin(BaseAdmin):
    list_display = (
        'title', 'client_link', 'manager_link',
        'status', 'expected_amount', 'probability',
        'duration_days', 'closed_at'
    )
    list_filter = ('status', 'manager', 'created_at')
    search_fields = ('title', 'client__name')
    raw_id_fields = ('manager',)
    fieldsets = (
        (None, {
            'fields': ('title', 'client', 'manager')
        }),
        (_('Детали'), {
            'fields': ('status', 'expected_amount', 'probability')
        }),
        (_('Даты'), {
            'fields': ('closed_at',),
            'classes': ('collapse',)
        }),
        (_('Системная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def client_link(self, obj):
        url = reverse('admin:core_client_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client)
    client_link.short_description = _('Клиент')

    def manager_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.manager.id])
        return format_html('<a href="{}">{}</a>', url, obj.manager.get_full_name())
    manager_link.short_description = _('Менеджер')

    def duration_days(self, obj):
        if obj.closed_at:
            return (obj.closed_at - obj.created_at).days
        return (timezone.now() - obj.created_at).days
    duration_days.short_description = _('Длительность (дней)')


@admin.register(Payment)
class PaymentAdmin(BaseAdmin):
    list_display = (
        'contract_link', 'date', 'amount',
        'is_confirmed', 'payment_method',
        'confirmation_date'
    )
    list_filter = ('is_confirmed', 'payment_method', 'date')
    search_fields = ('contract__number', 'transaction_id')
    list_editable = ('is_confirmed',)
    fieldsets = (
        (None, {
            'fields': ('contract', 'date', 'amount')
        }),
        (_('Статус'), {
            'fields': ('is_confirmed', 'confirmation_date')
        }),
        (_('Способ оплаты'), {
            'fields': ('payment_method', 'transaction_id')
        }),
        (_('Системная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def contract_link(self, obj):
        url = reverse('admin:core_contract_change', args=[obj.contract.id])
        return format_html('<a href="{}">{}</a>', url, obj.contract)
    contract_link.short_description = _('Договор')


@admin.register(DealTask)
class DealTaskAdmin(BaseAdmin):
    list_display = (
        'title', 'deal_link', 'assigned_to_link',
        'is_done', 'due_date', 'priority',
        'completed_at'
    )
    list_filter = ('is_done', 'priority', 'assigned_to')
    search_fields = ('title', 'deal__title')
    list_editable = ('is_done', 'priority')
    raw_id_fields = ('assigned_to',)
    fieldsets = (
        (None, {
            'fields': ('deal', 'assigned_to', 'title')
        }),
        (_('Детали'), {
            'fields': ('description', 'priority', 'due_date')
        }),
        (_('Статус'), {
            'fields': ('is_done', 'completed_at')
        }),
        (_('Системная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def deal_link(self, obj):
        url = reverse('admin:core_deal_change', args=[obj.deal.id])
        return format_html('<a href="{}">{}</a>', url, obj.deal)
    deal_link.short_description = _('Сделка')

    def assigned_to_link(self, obj):
        if not obj.assigned_to:
            return "-"
        url = reverse('admin:users_user_change', args=[obj.assigned_to.id])
        return format_html('<a href="{}">{}</a>', url, obj.assigned_to.get_full_name())
    assigned_to_link.short_description = _('Исполнитель')