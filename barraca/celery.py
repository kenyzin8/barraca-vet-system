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

from datetime import timedelta, datetime
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@app.task(name="Clean Calendar")
def clean_calendar():
    from record_management.models import Client, Pet
    from appointment_management.models import Appointment, DoctorSchedule
    try:
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
    except Exception as e:
        logger.error(f"Error in Clean Calendar: {e}")
    else:
        logger.info("Calendar Cleaned")
        return "Calendar Cleaned"

@app.task(name="Week Appointment Reminder")
def send_week_reminder():
    from appointment_management.models import Appointment
    try:
        appointments = Appointment.objects.filter(date__gte=datetime.now().date(), isActive=True, status='pending', weekly_reminder_sent=False)

        for appointment in appointments:
            if appointment.date - timedelta(weeks=1) == datetime.now().date():
                appointment.remindClient('weekly')
                logger.info(f'Week before appointment reminder sent to {appointment.client.full_name}. Date: {appointment.date} {appointment.timeOfTheDay}')

        if not appointments.exists():
            logger.info(f'No appointments to remind.')
            
    except Exception as e:
        logger.error(f"Error in Weekly Appointment Reminder: {e}")
    else:
        return "Week Before Reminder Called"

@app.task(name="Day Appointment Reminder")
def send_day_reminder():
    from appointment_management.models import Appointment
    try:
        appointments = Appointment.objects.filter(date__gte=datetime.now().date(), isActive=True, status='pending', daily_reminder_sent=False)

        for appointment in appointments:
            if appointment.date - timedelta(days=1) == datetime.now().date():
                appointment.remindClient('daily')
                logger.info(f'Day before appointment reminder sent to {appointment.client.full_name}. Date: {appointment.date} {appointment.timeOfTheDay}')

        if not appointments.exists():
            logger.info(f'No appointments to remind.')

    except Exception as e:
        logger.error(f"Error in Daily Appointment Reminder: {e}")
    else:
        return "Day Before Reminder Called"