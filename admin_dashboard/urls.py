from django.urls import path
from . import views

urlpatterns = [
    path('admin-vet/', views.admin_dashboard, name='admin-vet'),
]
