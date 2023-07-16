from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('admin/inventory/', permission_required('inventory.add_product', raise_exception=True)(views.product_list), name='product-list-page'),
    path('admin/inventory/product-type/', permission_required('inventory.add_product', raise_exception=True)(views.product_type_list), name='product-type-list-page'),
    path('admin/inventory/product-type/add/', permission_required('inventory.add_product', raise_exception=True)(views.add_type_page), name='add-type-page'),
    path('admin/inventory/product-type/delete/<int:type_id>/', permission_required('inventory.add_product', raise_exception=True)(views.delete_type_page), name='delete-type-page'),
    path('admin/inventory/add/', permission_required('inventory.add_product', raise_exception=True)(views.product_add), name='product-add-page'),
    path('admin/inventory/update/<int:product_id>/', permission_required('inventory.add_product', raise_exception=True)(views.product_update), name='product-update-page'),
    path('admin/inventory/delete/<int:product_id>/', permission_required('inventory.add_product', raise_exception=True)(views.delete_product), name='delete-product-page'),
    path('admin/inventory/check-quantity/<int:product_id>/', permission_required('inventory.add_product', raise_exception=True)(views.check_product_quantity), name='check-product-quantity-page'),
    path('admin/inventory/check-expiry/<int:product_id>/', permission_required('inventory.add_product', raise_exception=True)(views.check_product_expiry), name='check-product-expiry-page'),
    path('admin/inventory/reorder-list/', permission_required('inventory.add_product', raise_exception=True)(views.reorder_list), name='reorder-list-page'),
]