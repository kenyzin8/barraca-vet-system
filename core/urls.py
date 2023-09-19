from django.urls import path, re_path
from . import views

urlpatterns = [
    path('debug/', views.test, name='debug-page'),
    path('admin/inventory/get-notifications/', views.get_notifications, name='inventory-get-notification'),
    path('get_municipalities/', views.get_municipalities, name='get_municipalities'),
    path('get_barangays/', views.get_barangays, name='get_barangays'),
]