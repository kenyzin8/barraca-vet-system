from django.db import models
from django.contrib.auth.models import User
from datetime import date

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
    picture = models.ImageField(upload_to='public/images/')
    
    def __str__(self):
        return f"{self.name} ({self.species})"

    def age(self):
        today = date.today()
        years = today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        months = (today.year - self.birthday.year) * 12 + today.month - self.birthday.month - (today.day < self.birthday.day)
        days = (today - self.birthday).days

        if years > 0:
            age_string = f"{years} year{'s' if years > 1 else ''} old"
        elif months > 0:
            age_string = f"{months} month{'s' if months > 1 else ''} old"
        else:
            age_string = f"{days} day{'s' if days > 1 else ''} old"

        return age_string

    class Meta:
        verbose_name_plural = "Pets"