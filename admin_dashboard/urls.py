from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin-vet'),
    path('admin/sms-history', views.sms_history, name='sms-history'),
    path('admin/user-list', views.user_list, name='user-list-page'),
]
