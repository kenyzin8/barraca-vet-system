from django.contrib import admin
from .models import Product, Service, ProductType

def custom_delete_selected(modeladmin, request, queryset):
    if queryset.filter(name="Medicines").exists():
        modeladmin.message_user(request, "You cannot delete the 'Medicines' Product Type.", level='error')
        return
    queryset.delete()

custom_delete_selected.short_description = "Delete selected Product Types"

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'quantity_on_stock', 'type', 'batch_number', 'manufacturing_date', 'expiration_date', 'critical_level', 'price', 'active')
    readonly_fields = ('changes_log',)
    search_fields = ('product_name', 'type', 'price', 'batch_number')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'fee', 'control_number', 'active')
    readonly_fields = ('changes_log',)
    search_fields = ('service_type', 'fee', 'control_number', 'active')

class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    actions = [custom_delete_selected]

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Removes default "Delete selected" action
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

# Register the models in the admin site
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)
