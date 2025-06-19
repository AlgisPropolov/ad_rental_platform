from django.contrib import admin
from .models import Client, Asset, Contract
from .models import AvailabilitySlot

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('asset', 'start_date', 'end_date', 'is_booked')
    list_filter = ('asset', 'is_booked')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'contact_person', 'phone', 'email', 'created_at')
    search_fields = ('name', 'inn')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'location', 'is_active', 'created_at')
    list_filter = ('asset_type', 'is_active')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('client', 'asset', 'start_date', 'end_date', 'amount', 'signed')
    list_filter = ('signed', 'start_date', 'end_date')
    search_fields = ('client__name', 'asset__name')
from .models import Payment, Deal, DealTask

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'date', 'amount', 'is_confirmed')
    list_filter = ('is_confirmed',)

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'client__name')

@admin.register(DealTask)
class DealTaskAdmin(admin.ModelAdmin):
    list_display = ('deal', 'description', 'is_done', 'due_date')
    list_filter = ('is_done',)
