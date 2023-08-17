from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from getpass import getpass
from django.utils import timezone

from record_management.models import Client, Pet  # If not used, you can remove these imports.
from appointment_management.models import Appointment, DoctorSchedule

class Command(BaseCommand):
    help = 'Cleans the calendar.'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write('-' * 80)
            username = input("Please enter your username: ")
            password = getpass("Please enter your password: ")

            user = authenticate(username=username, password=password)

            if user is None or not user.is_superuser:
                self.stdout.write(self.style.ERROR("Authentication failed or user is not a superadmin. Exiting..."))
                return

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
            self.stdout.write(self.style.ERROR(f"Error in Clean Calendar: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("Calendar Cleaned"))
            self.stdout.write('-' * 80)