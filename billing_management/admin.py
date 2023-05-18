from django.contrib import admin
from .models import Billing, BillingProduct

class CustomBillingAdmin(admin.ModelAdmin):
    list_display = ('client', 'get_total', 'date_created')
    list_filter = ('client__first_name', 'client__last_name', 'client', 'date_created')
    search_fields = ('client__first_name', 'client__last_name', 'date_created')

admin.site.register(Billing, CustomBillingAdmin)
admin.site.register(BillingProduct)