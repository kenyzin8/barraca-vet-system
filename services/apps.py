from django.apps import AppConfig
from django.db import OperationalError

class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'

    def ready(self):
        from .models import Service 
        try:
            Service.ensure_checkup_exists()
        except OperationalError:
            pass