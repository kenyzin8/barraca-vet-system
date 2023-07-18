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
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.text
