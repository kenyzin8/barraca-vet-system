from django.urls import path
from . import views

urlpatterns = [
    path('admin/calendar', views.calendar, name='admin-calendar'),
    path('send_sms/', views.send_sms_to_client, name='send_sms_to_client'),
    path('set_appointment/add', views.set_appointment, name='set_appointment'),
    path('get_appointments/', views.get_appointments, name='get_appointments'),
    path('cancel_appointment/', views.cancel_appointment, name='cancel_appointment'),
    path('rebook_appointment/add', views.add_to_rebook_list, name='add_to_rebook_list'),
    path('rebook_appointment/move', views.rebook_appointment, name='rebook_appointment'),
    path('set_appointment/check-if-full', views.check_if_full, name='check_if_full'),
    path('set_appointment/get-pets', views.get_pets, name='get_pets'),
    path('set_appointment/done', views.set_appointment_done, name='mark_as_done'),
    path('disable_day', views.disable_day, name='disable_day'),
    path('get_disabled_days', views.get_disabled_days, name='get_disabled_days'),
    path('is_day_disabled', views.is_day_disabled, name='is_day_disabled'),
    path('enable_day', views.enable_day, name='enable_day'),
    #client
    path('appointments/', views.client_calendar, name='client_calendar'),
    path('appointments/add', views.set_appointment_client, name='client-add-appointment'),
    path('appointments/get', views.get_appointments_client, name='client-get-appointments'),
    path('appointments/check-appointments', views.is_all_my_pets_scheduled, name='is_all_my_pets_scheduled'),
    path('appointments/get-appountments-count', views.get_appointments_count, name='get_appointments_count'),
    path('appointments/get-pets', views.get_pets_client, name='client-get-pets'),
]