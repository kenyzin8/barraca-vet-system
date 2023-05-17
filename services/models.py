from django.db import models

# Create your models here.
class Service(models.Model):
    SERVICE_TYPES = (
        ('deworming', 'Deworming'),
        ('vaccination', 'Vaccination'),
        ('checkup', 'Check-up'),
        ('procedure', 'Procedure'),
        ('other', 'Other'),
    )

    REMARKS_TYPES = (
        ('without_medicine', 'Without Medicine'),
        ('with_medicine', 'With Medicine'),
    )

    service_type = models.CharField(max_length=50)
    fee = models.DecimalField(max_digits=8, decimal_places=2)
    remarks = models.CharField(max_length=20, choices=REMARKS_TYPES)

    def __str__(self):
        return f"{self.service_type} - {self.fee}"