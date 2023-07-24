from django.contrib import admin
from .models import Billing, BillingProduct, BillingService

class BillingServiceInline(admin.TabularInline):
    model = BillingService
    extra = 1

class BillingProductInline(admin.TabularInline):
    model = BillingProduct
    extra = 1

class BillingProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing', 'product', 'quantity')
    list_filter = ('billing__client__first_name', 'billing__client__last_name', 'billing')
    search_fields = ('billing__client__first_name', 'billing__client__last_name', 'billing')

class BillingServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing', 'service')
    list_filter = ('billing__client__first_name', 'billing__client__last_name', 'billing')
    search_fields = ('billing__client__first_name', 'billing__client__last_name', 'billing')

class CustomBillingAdmin(admin.ModelAdmin):
    inlines = (BillingProductInline, BillingServiceInline,)
    list_display = ('client', 'calculate_total', 'date_created')
    list_filter = ('client__first_name', 'client__last_name', 'client', 'date_created')
    search_fields = ('client__first_name', 'client__last_name', 'date_created')

    def calculate_total(self, obj):
        return obj.get_total()

    calculate_total.short_description = 'Total'

# admin.site.register(BillingService, BillingServiceAdmin)
# admin.site.register(BillingProduct, BillingProductAdmin)
admin.site.register(Billing, CustomBillingAdmin)
