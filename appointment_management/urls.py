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
    path('set_appointment/done', views.set_appointment_done, name='mark_as_done')
]