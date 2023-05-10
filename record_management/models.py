from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    two_auth_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Clients"

import datetime

class Pet(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    birthday = models.DateField()
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    color = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    picture = models.ImageField(upload_to='images/pets/')
    

    def __str__(self):
        return f"{self.name} ({self.species})"

    class Meta:
        verbose_name_plural = "Pets"