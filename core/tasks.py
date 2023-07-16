from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils import timezone

from record_management.models import Client, Pet
from appointment_management.models import Appointment
from core.semaphore import send_sms

