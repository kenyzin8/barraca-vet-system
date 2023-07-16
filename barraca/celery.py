from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barraca.settings')
app = Celery('barraca')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Manila')

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))

@app.task(name="debug print")
def print_hello_world():
    #send_sms("09772381588", "Welcome to Barraca Clinic!")
    print("Hello World")
    
    return "Hello World"

from datetime import timedelta, datetime
from django.utils import timezone

@app.task(name="Clean Calendar")
def clean_calendar():
    from record_management.models import Client, Pet
    from appointment_management.models import Appointment, DoctorSchedule
    
    def update_past_appointments():
        past_appointments = Appointment.objects.filter(date__lt=timezone.now().date(), isActive=True, status='pending')
        for appointment in past_appointments:
            appointment.status = 'done'
            appointment.isActive = False
            appointment.save()

    def update_past_doctor_schedules():
        past_doctor_schedules = DoctorSchedule.objects.filter(date__lt=timezone.now().date(), isActive=True)
        for schedule in past_doctor_schedules:
            schedule.isActive = False
            schedule.save()
            
    update_past_appointments()
    update_past_doctor_schedules()

    return "Calendar Cleaned"


@app.task(name="Weekly Appointment Reminder")
def send_weekly_reminder():
    from appointment_management.models import Appointment
    appointments = Appointment.objects.filter(date__gte=datetime.now().date(), isActive=True, status='pending')
    for appointment in appointments:
        if appointment.date - timedelta(weeks=1) == datetime.now().date():
            appointment.remindClient()

    return "Weekly Reminder Sent"


@app.task(name="Daily Appointment Reminder")
def send_daily_reminder():
    from appointment_management.models import Appointment
    appointments = Appointment.objects.filter(date__gte=datetime.now().date(), isActive=True, status='pending')
    for appointment in appointments:
        if appointment.date - timedelta(days=1) == datetime.now().date():
            appointment.remindClient()
    
    return "Daily Reminder Sent"
