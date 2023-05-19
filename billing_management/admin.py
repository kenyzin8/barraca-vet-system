from django.contrib import admin
from .models import Billing, BillingProduct, BillingService

class BillingServiceInline(admin.TabularInline):
    model = BillingService
    extra = 1

class BillingProductInline(admin.TabularInline):
    model = BillingProduct
    extra = 1

class CustomBillingAdmin(admin.ModelAdmin):
    inlines = (BillingProductInline, BillingServiceInline,)
    list_display = ('client', 'get_total', 'date_created')
    list_filter = ('client__first_name', 'client__last_name', 'client', 'date_created')
    search_fields = ('client__first_name', 'client__last_name', 'date_created')

admin.site.register(Billing, CustomBillingAdmin)