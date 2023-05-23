from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/inventory/get-notifications/', views.get_notifications, name='inventory-get-notification'),
]