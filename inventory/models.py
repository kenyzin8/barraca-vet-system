from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator

class ProductType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Product Type"
        verbose_name_plural = "Product Types"

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    quantity_on_stock = models.DecimalField(default=1.00, max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    critical_level = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} - {self.price}"

    def is_product_critical(self):
        if self.quantity_on_stock <= self.critical_level:
            return True
        else:
            return False