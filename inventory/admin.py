from django.contrib import admin
from .models import Product, ProductType
# Register your models here.

class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity_on_stock', 'type', 'batch_number', 'manufacturing_date', 'expiration_date', 'critical_level', 'price', 'active')
    readonly_fields = ('original_product_name',)
    search_fields = ('product_name', 'type', 'price', 'batch_number')

admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
