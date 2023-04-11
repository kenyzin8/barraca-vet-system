from django.urls import path
from . import views

urlpatterns = [
    path('admin-vet/calendar', views.calendar, name='admin-calendar'),
]
