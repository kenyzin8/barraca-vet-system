from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/bill/', views.bill, name='billing-page'),
    path('admin/bill/client/<int:client_id>/', views.bill_client, name='billing-client-page'),
    path('admin/bill/post/', views.post_bill, name='post-bill'),
    path('admin/bill/view/<int:bill_id>/', views.view_bill, name='view-bill-page'),
    path('admin/sales/', views.sales, name='sales-page'),
]