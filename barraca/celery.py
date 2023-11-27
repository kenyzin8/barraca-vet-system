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
        current_datetime = timezone.now()
        current_date = current_datetime.date()

        def update_past_appointments():
            past_appointments = Appointment.objects.filter(date__lt=current_date, isActive=True, status='pending')
            for appointment in past_appointments:
                appointment.status = 'done'
                appointment.isActive = False
                appointment.save()

        def update_past_doctor_schedules():
            past_doctor_schedules = DoctorSchedule.objects.filter(date__lt=current_date, isActive=True)
            for schedule in past_doctor_schedules:
                schedule.isActive = False
                schedule.save()
                
        update_past_appointments()
        update_past_doctor_schedules()

        logger.info(f'Current DateTime: {current_datetime}')
        logger.info(f'Current Date: {current_date}')
        
    except Exception as e:
        logger.error(f"Error in Clean Calendar: {e}")
    else:
        logger.info("Calendar Cleaned")
        return "Calendar Cleaned"

@app.task(name="One Hour Appointment Reminder")
def send_one_hour_reminder():
    from appointment_management.models import Appointment
    try:
        now = timezone.now()

        appointments = Appointment.objects.filter(
            date=now.date(), 
            time__gte=now.time(), 
            time__lt=(now + timedelta(hours=1)).time(), 
            isActive=True, 
            status='pending',
            one_hour_reminder_sent=False
        )

        total_sent = 0

        for appointment in appointments:
            total_sent += 1
            appointment.remindClient('hourly')
            logger.info(f'One hour before appointment reminder sent to {appointment.client.full_name}. Date: {appointment.date}, Time: {appointment.time}')

        if total_sent == 0:
            logger.info('No appointments to remind for the next hour.')
            
    except Exception as e:
        logger.error(f"Error in Hourly Appointment Reminder: {e}")
    else:
        return "One Hour Before Reminder Called"

@app.task(name="Today Appointment Reminder")
def send_today_reminder():
    from appointment_management.models import Appointment
    try:
        today = timezone.now().date()

        appointments = Appointment.objects.filter(
            date=today,
            isActive=True, 
            status='pending',
            today_reminder_sent=False
        )

        total_sent = 0

        for appointment in appointments:
            total_sent += 1
            appointment.remindClient('today')
            logger.info(f'Today appointment reminder sent to {appointment.client.full_name}. Date: {appointment.date}, Time: {appointment.time}')

        if total_sent == 0:
            logger.info('No appointments to remind for today.')
            
    except Exception as e:
        logger.error(f"Error in Daily Appointment Reminder: {e}")
    else:
        return "Today Reminder Called"

@app.task(name="Week Appointment Reminder")
def send_week_reminder():
    from appointment_management.models import Appointment
    try:
        appointments = Appointment.objects.filter(date__gte=datetime.now().date(), isActive=True, status='pending', weekly_reminder_sent=False)

        total_sent = 0

        for appointment in appointments:
            if appointment.date - timedelta(weeks=1) == datetime.now().date():
                total_sent += 1
                appointment.remindClient('weekly')
                logger.info(f'Week before appointment reminder sent to {appointment.client.full_name}. Date: {appointment.date} {appointment.timeOfTheDay}')

        if total_sent == 0:
            logger.info(f'No appointments to remind for week before.')
            
    except Exception as e:
        logger.error(f"Error in Weekly Appointment Reminder: {e}")
    else:
        return "Week Before Reminder Called"

@app.task(name="Day Appointment Reminder")
def send_day_reminder():
    from appointment_management.models import Appointment
    try:
        appointments = Appointment.objects.filter(date__gte=datetime.now().date(), isActive=True, status='pending', daily_reminder_sent=False)

        total_sent = 0

        for appointment in appointments:
            if appointment.date - timedelta(days=1) == datetime.now().date():
                total_sent += 1
                appointment.remindClient('daily')
                logger.info(f'Day before appointment reminder sent to {appointment.client.full_name}. Date: {appointment.date} {appointment.timeOfTheDay}')

        if total_sent == 0:
            logger.info(f'No appointments to remind for day before.')

    except Exception as e:
        logger.error(f"Error in Daily Appointment Reminder: {e}")
    else:
        return "Day Before Reminder Called"