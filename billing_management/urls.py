from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('admin/bill/', permission_required('billing_management.add_billing', raise_exception=True)(views.bill), name='billing-page'),
    # path('admin/bill/client/', views.bill_client, name='billing-client-page'),
    path('admin/bill/post/', permission_required('billing_management.add_billing', raise_exception=True)(views.post_bill), name='post-bill'),
    path('admin/bill/view/<int:bill_id>/', permission_required('billing_management.add_billing', raise_exception=True)(views.view_bill), name='view-bill-page'),
    path('admin/sales/', permission_required('billing_management.add_billing', raise_exception=True)(views.sales), name='sales-page'),
]