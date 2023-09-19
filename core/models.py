from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from record_management.models import Client

class SMSLogs(models.Model):
    text = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    sms_type = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.text} - {self.client.full_name}'

    class Meta:
        verbose_name_plural = 'SMS Logs'
        

class Notification(models.Model):
    CRITICAL = 'critical'
    OUT_OF_STOCK = 'out_of_stock'
    EXPIRED = 'expired'
    
    NOTIFICATION_TYPES = [
        (CRITICAL, 'Critical Level'),
        (OUT_OF_STOCK, 'Out of Stock'),
        (EXPIRED, 'Expired'),
    ]

    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default="none")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text

class Region(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Regions"

class Province(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Provinces"

class Municipality(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities"

class Barangay(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Barangays"