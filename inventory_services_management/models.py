from django.db import models
from inventory.models import Product as InventoryProduct
from inventory.models import ProductType as InventoryProductType
from services.models import Service as ServicesService

class Product(InventoryProduct):
    class Meta:
        proxy = True

class ProductType(InventoryProductType):
    class Meta:
        proxy = True
        verbose_name = 'Product Type'

class Service(ServicesService):
    class Meta:
        proxy = True
