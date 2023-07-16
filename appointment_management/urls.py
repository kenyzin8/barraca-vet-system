from django.urls import path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('admin/calendar/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.calendar), name='admin-calendar'),
    path('admin/send_sms/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.send_sms_to_client), name='send_sms_to_client'),
    path('admin/set_appointment/add/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.set_appointment), name='set_appointment'),
    path('admin/get_appointments/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.get_appointments), name='get_appointments'),
    path('admin/cancel_appointment/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.cancel_appointment), name='cancel_appointment'),
    path('admin/rebook_appointment/add/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.add_to_rebook_list), name='add_to_rebook_list'),
    path('admin/rebook_appointment/move/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.rebook_appointment), name='rebook_appointment'),
    path('admin/set_appointment/check-if-full/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.check_if_full), name='check_if_full'),
    path('admin/set_appointment/get-pets/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.get_pets), name='get_pets'),
    path('admin/set_appointment/done/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.set_appointment_done), name='mark_as_done'),
    path('admin/disable_day/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.disable_day), name='disable_day'),
    path('admin/get_disabled_days/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.get_disabled_days), name='get_disabled_days'),
    path('admin/is_day_disabled/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.is_day_disabled), name='is_day_disabled'),
    path('admin/enable_day/', permission_required('appointment_management.add_appointment', raise_exception=True)(views.enable_day), name='enable_day'),
    #client
    path('appointments/', views.client_calendar, name='client_calendar'),
    path('appointments/add/', views.set_appointment_client, name='client-add-appointment'),
    path('appointments/get/', views.get_appointments_client, name='client-get-appointments'),
    path('appointments/check-appointments/', views.is_all_my_pets_scheduled, name='is_all_my_pets_scheduled'),
    path('appointments/get-appountments-count/', views.get_appointments_count, name='get_appointments_count'),
    path('appointments/get-pets/', views.get_pets_client, name='client-get-pets'),
]