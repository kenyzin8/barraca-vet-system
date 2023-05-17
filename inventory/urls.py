from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/inventory/', views.product_list, name='product-list-page'),
    path('admin/inventory/add/', views.product_add, name='product-add-page'),
    path('admin/inventory/update/<int:product_id>/', views.product_update, name='product-update-page'),
    path('admin/inventory/delete/<int:product_id>/', views.delete_product, name='delete-product-page'),
]