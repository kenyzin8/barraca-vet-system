from django.contrib import admin
from .models import Service

# Register your models here.

# class ServiceRemarksAdmin(admin.ModelAdmin):
#     list_display = ('remarks', 'active')
#     search_fields = ('remarks', 'active')

# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ('service_type', 'fee', 'remarks', 'control_number', 'active')
#     readonly_fields = ('changes_log',)
#     search_fields = ('service_type', 'fee', 'remarks', 'control_number', 'active')

# #admin.site.register(ServiceRemarks, ServiceRemarksAdmin)
# admin.site.register(Service, ServiceAdmin)