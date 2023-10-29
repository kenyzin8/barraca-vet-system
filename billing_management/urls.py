from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('admin/bill/', permission_required('billing_management.add_billing', raise_exception=True)(views.bill), name='billing-page'),
    # path('admin/bill/client/', views.bill_client, name='billing-client-page'),
    path('admin/bill/cancel/', permission_required('billing_management.add_billing', raise_exception=True)(views.cancel_bill), name='cancel-bill'),
    path('admin/bill/post/', permission_required('billing_management.add_billing', raise_exception=True)(views.post_bill), name='post-bill'),
    path('admin/bill/process-unpaid-bill/', permission_required('billing_management.add_billing', raise_exception=True)(views.process_unpaid_bill), name='process-unpaid-bill'),
    path('admin/bill/cancel-unpaid-bill/', permission_required('billing_management.add_billing', raise_exception=True)(views.cancel_unpaid_bill), name='cancel-unpaid-bill'),
    path('admin/bill/unpaid/post', permission_required('billing_management.add_billing', raise_exception=True)(views.mark_unpaid_bill_as_paid), name='post-unpaid-bill'),
    #path('admin/sales/<int:bill_id>/', permission_required('billing_management.view_billing', raise_exception=True)(views.view_bill), name='view-bill-page'),
    path('admin/sales/<int:bill_id>/', views.view_bill, name='view-bill-page'),
    path('admin/sales/unpaid/<int:bill_id>/', views.view_unpaid_bill, name='unpaid-bill-page'),
    #path('admin/sales/', permission_required('billing_management.view_billing', raise_exception=True)(views.sales), name='sales-page'),
    path('admin/sales/', views.sales, name='sales-page'),
]