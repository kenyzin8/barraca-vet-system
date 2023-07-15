from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils import timezone

from record_management.models import Client, Pet
from appointment_management.models import Appointment
from core.semaphore import send_sms

@shared_task
def print_hello_world():
    #send_sms("09772381588", "Welcome to Barraca Clinic!")
    print("Hello World")
    return "Hello World"

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

@shared_task
def update_past_appointments():
    update_past_appointments()
    update_past_doctor_schedules()
    return "Calendar Updated"

@shared_task
def send_weekly_reminder():
    appointments = Appointment.objects.filter(date__gte=datetime.now().date())
    for appointment in appointments:
        if appointment.date - timedelta(weeks=1) == datetime.now().date():
            appointment.remindClient()
    return "Weekly Reminder Sent"


@shared_task
def send_daily_reminder():
    appointments = Appointment.objects.filter(date__gte=datetime.now().date())
    for appointment in appointments:
        if appointment.date - timedelta(days=1) == datetime.now().date():
            appointment.remindClient()
    return "Daily Reminder Sent"