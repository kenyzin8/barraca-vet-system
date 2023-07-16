from django.urls import path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin-vet'),
    path('admin/sms-history/', views.sms_history, name='sms-history'),
    path('admin/user-list/', permission_required('record_management.add_client', raise_exception=True)(views.user_list), name='user-list-page'),
]
