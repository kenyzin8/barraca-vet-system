from django.db import models
from record_management.models import Pet, Client
from services.models import Service
from core.semaphore import send_sms

class Appointment(models.Model):

    time_of_the_day_choices = [('morning', 'Morning'), ('afternoon', 'Afternoon')]
    status_choices = [('pending', 'Pending'), ('rebook', 'Rebook'), ('cancelled', 'Cancelled'), ('done', 'Done')]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    timeOfTheDay = models.CharField(max_length=10, choices=time_of_the_day_choices)
    date = models.DateField()
    purpose = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=status_choices)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.client} ({self.pet}) - {self.date} - {self.timeOfTheDay}'

    def setActive(self, isActive):
        self.isActive = isActive

    def setActiveOnStatus(self):
        if self.status == 'Cancelled':
            self.isActive = False
        else:
            self.isActive = True

    def remindClient(self):
        phone_number = self.client.contact_number
        message = f'Hi {self.client.full_name}, this is a reminder for your {self.purpose.service_type} Appointment for {self.pet.name} on {self.date} at {self.timeOfTheDay}. Thank you!'
        send_sms(phone_number, message)

    def getTimeOfDayColor(self):
        if self.timeOfTheDay == 'morning':
            return 'default'
        else:
            return 'green'

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"