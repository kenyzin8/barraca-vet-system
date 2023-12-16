from django.db import models

from inventory.models import Product
from services.models import Service
from record_management.models import Client
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from record_management.models import PrescriptionMedicines, PetTreatment
from collections import defaultdict

import re

def find_similar_service(lab_test_name):
    similar_service = None
    for service in Service.objects.all():
        if is_similar(lab_test_name, service.service_type):
            similar_service = service
            break
    return similar_service

def is_similar(string1, string2):
    def remove_parentheses(s):
        return s.replace('(', '').replace(')', '')

    string1_clean = remove_parentheses(string1)
    string2_clean = remove_parentheses(string2)

    words1 = set(string1_clean.lower().split())
    words2 = set(string2_clean.lower().split())

    for word in words1:
        if word in words2:
            return True

    return False

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
    isActive = models.BooleanField(default=True)
    isPaid = models.BooleanField(default=False)
    treatments = models.ManyToManyField(PetTreatment, blank=True)
    
    def get_total(self):
        total = 0
        for service in self.billing_services.all():
            total += service.price_at_time_of_purchase * service.quantity
        for billing_product in self.billing_products.all():
            total += billing_product.price_at_time_of_purchase * billing_product.quantity

        return total

    def include_similar_services(self):
        temp_service_counts = defaultdict(int)

        for treatment in self.treatments.all():
            for lab_result in treatment.lab_results.all():
                similar_service = find_similar_service(lab_result.result_name)
                if similar_service:
                    temp_service_counts[similar_service.id] += 1

        for service_id, count in temp_service_counts.items():
            billing_service = self.billing_services.filter(service_id=service_id).first()
            if billing_service:
                billing_service.quantity = count
                billing_service.save()
            else:
                similar_service = Service.objects.get(id=service_id)
                BillingService.objects.create(
                    billing=self,
                    service=similar_service,
                    price_at_time_of_purchase=similar_service.fee,
                    quantity=count
                )

        self.save()

    def get_billing_number(self):
        return format_billing_number(self.id)

    def __str__(self):
        return self.client.full_name + " - Total: ₱ " + str(self.get_total())

    class Meta:
        verbose_name_plural = "Bills"

class BillingProduct(models.Model):
    """
    BILL PRODUCT CART
    """
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='billing_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    prescription_details = models.ForeignKey(PrescriptionMedicines, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(default=1.000, max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    
    price_at_time_of_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        #print(self.pk)
        if not self.pk:
            self.price_at_time_of_purchase = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.billing} - {self.product} ({self.quantity})"

    class Meta:
        verbose_name_plural = "Billing Products"

class BillingService(models.Model):
    """
    BILL SERVICE CART
    """
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='billing_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price_at_time_of_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        #print(self.pk)
        if not self.pk:
            self.price_at_time_of_purchase = self.service.fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.billing} - {self.service}"

    class Meta:
        verbose_name_plural = "Billing Services"