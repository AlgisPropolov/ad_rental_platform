from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import (
    Client, Asset, AvailabilitySlot, Deal, 
    Contract, Payment, DealTask, Tag, ContractAsset
)


class IsActiveFilter(SimpleListFilter):
    title = _('Активность')
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Активные')),
            ('no', _('Неактивные')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.active()
        if self.value() == 'no':
            return queryset.exclude(is_active=True)
        return queryset


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'is_vip', 'is_active')
    list_filter = (IsActiveFilter, 'is_vip', 'manager')
    search_fields = ('name', 'contact_person', 'phone', 'email', 'inn')
    raw_id_fields = ('manager',)
    list_editable = ('is_active', 'is_vip')
    fieldsets = (
        (None, {
            'fields': ('name', 'inn', 'is_active', 'is_vip')
        }),
        (_('Контактная информация'), {
            'fields': ('contact_person', 'phone', 'email')
        }),
        (_('Дополнительно'), {
            'fields': ('manager', 'notes')
        }),
    )


class ContractInline(admin.TabularInline):
    model = ContractAsset
    extra = 1
    raw_id_fields = ('asset', 'slot')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'zone', 'location', 'daily_rate', 'is_active')
    list_filter = ('asset_type', 'zone', IsActiveFilter)
    search_fields = ('name', 'location')
    list_editable = ('is_active', 'daily_rate')
    filter_horizontal = ('tags',)
    inlines = [ContractInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'asset_type', 'is_active')
        }),
        (_('Размещение'), {
            'fields': ('zone', 'location')
        }),
        (_('Финансы'), {
            'fields': ('daily_rate',)
        }),
        (_('Дополнительно'), {
            'fields': ('tags', 'notes')
        }),
    )


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('asset', 'start_date', 'end_date', 'is_available', 'reserved_by')
    list_filter = ('is_available', 'asset__asset_type')
    raw_id_fields = ('asset', 'reserved_by')
    date_hierarchy = 'start_date'
    search_fields = ('asset__name',)


class ContractAssetInline(admin.TabularInline):
    model = ContractAsset
    extra = 1
    raw_id_fields = ('asset', 'slot')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('date', 'amount', 'payment_method', 'status', 'is_confirmed')
    readonly_fields = ('date', 'amount', 'payment_method', 'status', 'is_confirmed')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'start_date', 'end_date', 'total_amount', 'is_active')
    list_filter = ('is_active', 'payment_type', 'signed')
    search_fields = ('number', 'client__name')
    raw_id_fields = ('client', 'deal')
    date_hierarchy = 'start_date'
    inlines = [ContractAssetInline, PaymentInline]
    fieldsets = (
        (None, {
            'fields': ('number', 'client', 'deal', 'is_active')
        }),
        (_('Период действия'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Финансы'), {
            'fields': ('total_amount', 'payment_type')
        }),
        (_('Подписание'), {
            'fields': ('signed', 'signed_date', 'document')
        }),
    )


class StatusFilter(SimpleListFilter):
    title = _('Статус')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Deal.Status.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'manager', 'status', 'expected_amount', 'probability', 'created_at')
    list_filter = (StatusFilter, 'probability', 'manager')
    search_fields = ('title', 'client__name')
    raw_id_fields = ('client', 'manager')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'client', 'manager', 'status')
        }),
        (_('Финансы'), {
            'fields': ('expected_amount', 'probability')
        }),
        (_('Закрытие'), {
            'fields': ('closed_at',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.status in [Deal.Status.WON, Deal.Status.LOST] and not obj.closed_at:
            obj.closed_at = timezone.now()
        super().save_model(request, obj, form, change)


class PaymentStatusFilter(SimpleListFilter):
    title = _('Статус платежа')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Payment.Status.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'amount', 'date', 'payment_method', 'status', 'is_confirmed')
    list_filter = (PaymentStatusFilter, 'payment_method', 'is_confirmed')
    search_fields = ('contract__number', 'transaction_id')
    raw_id_fields = ('contract',)
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('contract', 'amount', 'date')
        }),
        (_('Детали платежа'), {
            'fields': ('payment_method', 'status', 'transaction_id')
        }),
        (_('Подтверждение'), {
            'fields': ('is_confirmed', 'confirmation_date', 'receipt')
        }),
        (_('Примечания'), {
            'fields': ('notes',)
        }),
    )


class PriorityFilter(SimpleListFilter):
    title = _('Приоритет')
    parameter_name = 'priority'

    def lookups(self, request, model_admin):
        return DealTask.Priority.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(priority=self.value())
        return queryset


@admin.register(DealTask)
class DealTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'deal', 'assigned_to', 'due_date', 'priority', 'is_done')
    list_filter = (PriorityFilter, 'is_done', 'assigned_to')
    search_fields = ('title', 'deal__title')
    raw_id_fields = ('deal', 'assigned_to')
    date_hierarchy = 'due_date'
    fieldsets = (
        (None, {
            'fields': ('deal', 'assigned_to', 'title')
        }),
        (_('Описание'), {
            'fields': ('description',)
        }),
        (_('Статус'), {
            'fields': ('is_done', 'completed_at')
        }),
        (_('Сроки'), {
            'fields': ('due_date', 'priority')
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


@admin.register(ContractAsset)
class ContractAssetAdmin(admin.ModelAdmin):
    list_display = ('contract', 'asset', 'price', 'slot')
    raw_id_fields = ('contract', 'asset', 'slot')
    search_fields = ('contract__number', 'asset__name')