from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin-vet'),
    path('admin/sms-history', views.sms_history, name='sms-history'),
]
