from django.apps import AppConfig
from django.db import OperationalError

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        from .models import ProductType
        try:
            if not ProductType.objects.filter(name="Medicines").exists():
                ProductType.objects.create(name="Medicines")
        except OperationalError:
            pass