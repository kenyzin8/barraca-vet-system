from django.db import models

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
    quantity_on_stock = models.IntegerField()
    type = models.CharField(max_length=50, choices=TYPES, default='tablets')
    batch_number = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    critical_level = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_name