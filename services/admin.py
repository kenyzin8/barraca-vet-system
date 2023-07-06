from django.contrib import admin
from .models import Service

# Register your models here.
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'fee', 'remarks', 'control_number', 'active')
    #readonly_fields = ('original_service', 'control_number', 'active')
    search_fields = ('service_type', 'fee', 'remarks', 'control_number', 'active')

admin.site.register(Service, ServiceAdmin)