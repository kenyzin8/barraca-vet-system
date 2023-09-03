from django.apps import AppConfig
from django.db import OperationalError

class AppointmentManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointment_management'
    verbose_name = 'Appointment Management'

    def ready(self):
        from .models import MaximumAppointment
        try:
            MaximumAppointment.load()
        except OperationalError:
            pass
