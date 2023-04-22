from celery import shared_task
import time

from .semaphore import send_sms

@shared_task
def print_hello_world():
    send_sms('09772381588', 'Sent from Heroku Server')
