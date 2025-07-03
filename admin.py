from django.contrib import admin
from .models import Client, AdSpace, Contract

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'contact_person')

@admin.register(AdSpace)
class AdSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'location', 'daily_rate', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('location',)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'ad_space', 'start_date', 'end_date', 'total_amount')
    list_filter = ('start_date', 'end_date')
    search_fields = ('client__name', 'ad_space__location')