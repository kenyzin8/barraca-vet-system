from django.contrib import admin
from .models import Product
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity_on_stock', 'type', 'batch_number', 'manufacturing_date', 'expiration_date', 'critical_level', 'price')
    search_fields = ('product_name', 'type', 'price', 'batch_number')

admin.site.register(Product, ProductAdmin)