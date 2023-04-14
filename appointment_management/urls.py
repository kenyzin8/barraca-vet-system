from django.urls import path
from . import views

urlpatterns = [
    path('admin-vet/calendar', views.calendar, name='admin-calendar'),
    path('send_sms/', views.send_sms_to_client, name='send_sms_to_client'),
]
