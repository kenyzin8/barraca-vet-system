from django.urls import path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin-vet'),
    path('admin/sms-history/', views.sms_history, name='sms-history'),
    path('admin/user-list/', permission_required('record_management.add_client', raise_exception=True)(views.user_list), name='user-list-page'),
    path('admin/user-list/update-user/<int:userID>/', permission_required('record_management.add_client', raise_exception=True)(views.update_user), name='update-user-page'),
    path('admin/user-list/update-user/2FA/<int:userID>/', permission_required('record_management.add_client', raise_exception=True)(views.update_2fa), name='update-user-2fa-page'),
    path('admin/user-list/ban-user/<int:userID>/', permission_required('record_management.add_client', raise_exception=True)(views.ban_user), name='ban-user-page'),
    path('admin/user-list/unban-user/<int:userID>/', permission_required('record_management.add_client', raise_exception=True)(views.unban_user), name='unban-user-page'),
    path('admin/user-list/promote-user/<int:userID>/', permission_required('record_management.add_client', raise_exception=True)(views.promote_user), name='promote-user-page'),
    path('admin/user-list/demote-user/<int:userID>/', permission_required('record_management.add_client', raise_exception=True)(views.demote_user), name='demote-user-page'),
]
