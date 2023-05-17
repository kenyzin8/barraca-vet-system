from django.contrib import admin
from .models import Service

# Register your models here.
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'fee', 'remarks')
    search_fields = ('service_type', 'fee', 'remarks')

admin.site.register(Service, ServiceAdmin)