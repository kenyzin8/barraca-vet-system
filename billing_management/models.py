from django.db import models

from inventory.models import Product
from services.models import Service
from record_management.models import Client
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator

def format_billing_number(id):
    id_str = str(id)
    padding_length = (3 - len(id_str) % 3) % 3
    padded_id_str = '0' * padding_length + id_str
    return '-'.join(padded_id_str[i:i+3] for i in range(0, len(padded_id_str), 3))

class Billing(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, through='BillingService')
    products = models.ManyToManyField(Product, through='BillingProduct')
    date_created = models.DateTimeField(auto_now_add=True)
    
    def get_total(self):
        total = 0
        for service in self.services.all():
            total += service.fee
        for billing_product in self.billing_products.all():
            total += billing_product.product.price * billing_product.quantity
        return total

    def get_billing_number(self):
        return format_billing_number(self.id)

    def __str__(self):
        return self.client.full_name + " - Total: ₱ " + str(self.get_total())

        # update inventory quantity tomorrow

class BillingProduct(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='billing_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(default=1.000, max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.billing} - {self.product} ({self.quantity})"

class BillingService(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='billing_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.billing} - {self.service}"