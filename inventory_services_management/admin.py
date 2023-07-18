from django.contrib import admin

# Register your models here.
from .models import Product, Service, ProductType

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'quantity_on_stock', 'type', 'batch_number', 'manufacturing_date', 'expiration_date', 'critical_level', 'price', 'active')
    readonly_fields = ('changes_log',)
    search_fields = ('product_name', 'type', 'price', 'batch_number')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'fee', 'remarks', 'control_number', 'active')
    readonly_fields = ('changes_log',)
    search_fields = ('service_type', 'fee', 'remarks', 'control_number', 'active')

class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')

admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)