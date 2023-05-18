from django.db import models

from inventory.models import Product
from services.models import Service
from record_management.models import Client

class Billing(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    products = models.ManyToManyField(Product, through='BillingProduct')
    date_created = models.DateTimeField(auto_now_add=True)
    
    def get_total(self):
        total = 0
        for service in self.services.all():
            total += service.fee
        for billing_product in self.billing_products.all():
            total += billing_product.product.price * billing_product.quantity
        return total

    def __str__(self):
        return self.client.first_name + " " + self.client.last_name + " " + str(self.get_total())

class BillingProduct(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='billing_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.billing} - {self.product} ({self.quantity})"