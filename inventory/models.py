from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
# Create your models here.
class Product(models.Model):
    TYPES = (
        ('tablets', 'Tablets'),
        ('syrups', 'Syrups'),
        ('injections', 'Injections'),
        ('ointments', 'Ointments'),
        ('capsules', 'Capsules'),
        ('catfood', 'Catfood'),
        ('dogfood', 'Dogfood'),
    )

    product_name = models.CharField(max_length=255)
    quantity_on_stock = models.DecimalField(default=1.000, max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    type = models.CharField(max_length=50, choices=TYPES, default='tablets')
    batch_number = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    critical_level = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} - {self.price}"