from django.urls import path
from . import views

urlpatterns = [
    path('customer-dashboard/', views.customer_dashboard, name='customer-dashboard'),
]
