from django.db import models
from record_management.models import Pet, Client
from core.models import SMSLogs
from services.models import Service
from core.semaphore import send_sms
from .utils import time_choices
from datetime import time

class MaximumAppointment(models.Model):
    max_appointments = models.IntegerField(default=8)

    def __str__(self):
        return f'{self.max_appointments}'

    def save(self, *args, **kwargs):
        self.pk = 1
        super(MaximumAppointment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Maximum Appointment"
        verbose_name_plural = "Maximum Appointments"

class DateSlot(models.Model):
    date = models.DateField()
    
    morning_slots = models.IntegerField(default=4)
    afternoon_slots = models.IntegerField(default=4)
    
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.date}'

    class Meta:
        verbose_name = "Date Slot"
        verbose_name_plural = "Date Slots"

class DoctorSchedule(models.Model):
    time_of_the_day_choices = [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('whole_day', 'Whole Day')]
    date = models.DateField()
    reason = models.CharField(max_length=100)
    isActive = models.BooleanField(default=True)
    timeOfTheDay = models.CharField(max_length=10, choices=time_of_the_day_choices)

    def __str__(self):
        return f'{self.date} - {self.timeOfTheDay}'

    def send_message_to_client(self):
        if self.timeOfTheDay == 'whole_day':
            appointments = Appointment.objects.filter(date=self.date, isActive=True, status='pending')
        else:
            appointments = Appointment.objects.filter(date=self.date, timeOfTheDay=self.timeOfTheDay, isActive=True, status='pending')

        for appointment in appointments:
            send_sms(appointment.client.contact_number, f'Hello {appointment.client.full_name}, your appointment on {self.date} {appointment.timeOfTheDay} has been cancelled due to {self.reason}. Please rebook your appointment on our webiste or contact the clinic to do it for you. Thank you!')

    class Meta:
        verbose_name = "Doctor Schedule"
        verbose_name_plural = "Doctor Schedules"

class Appointment(models.Model):
    status_choices = [('pending', 'Pending'), ('rebook', 'Rebook'), ('cancelled', 'Cancelled'), ('done', 'Done'), ('petdeleted', 'Pet Deleted')]
    time_of_the_day_choices = [('morning', 'Morning'), ('afternoon', 'Afternoon')]
    # 7:30 AM to 5:00 PM and each is 30 minutes
    time_choices = time_choices

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    timeOfTheDay = models.CharField(max_length=10, choices=time_of_the_day_choices)
    date = models.DateField()
    time = models.TimeField(default='00:00:00')
    purpose = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=status_choices)
    isActive = models.BooleanField(default=True)

    weekly_reminder_sent = models.BooleanField(default=False)
    daily_reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.client} ({self.pet}) - {self.date} - {self.time}'

    def getAppointmentDate(self):
        time = self.time.strftime('%I:%M %p')
        date = self.date.strftime('%B %d, %Y')
        return f'{date} {time}'

    def setActive(self, isActive):
        self.isActive = isActive

    def getDate(self):
        return self.date.strftime('%B %d, %Y')

    def setActiveOnStatus(self):
        if self.status == 'Cancelled':
            self.isActive = False
        else:
            self.isActive = True

    def remindClient(self, reminder_type):
        phone_number = self.client.contact_number
        formatted_time = self.time.strftime('%I:%M %p')
        message = f'Hi {self.client.full_name}, this is a reminder for your {self.purpose.service_type} appointment about {self.pet.name} on {self.date} at {formatted_time}. Thank you!'
        send_sms(phone_number, message)

        SMSLogs.objects.create(
            text = message,
            client = self.client,
            sms_type = reminder_type
        )
    
        if reminder_type == 'weekly':
            self.weekly_reminder_sent = True
        elif reminder_type == 'daily':
            self.daily_reminder_sent = True
        elif reminder_type == 'renotify':
            pass
        self.save()

    def remindClientCancel(self, reason):
        phone_number = self.client.contact_number
        formatted_time = self.time.strftime('%I:%M %p')
        message = f'Hi {self.client.full_name}, this is a reminder for your {self.purpose.service_type} appointment about {self.pet.name} on {self.date} at {formatted_time} has been cancelled. Due to {reason}. Thank you!'
        send_sms(phone_number, message)

        SMSLogs.objects.create(
            text = message,
            client = self.client,
            sms_type = 'cancel'
        )

    def remindClientRebook(self, newDate, newTime):
        phone_number = self.client.contact_number
        formatted_time = self.time.strftime('%I:%M %p')
        formatted_new_time = newTime.strftime('%I:%M %p')
        message = f'Hi {self.client.full_name}, this is a reminder for your {self.purpose.service_type} appointment about {self.pet.name} on {self.date} at {formatted_time} has been rebooked to {newDate} {formatted_new_time}. Thank you!'
        send_sms(phone_number, message)

        SMSLogs.objects.create(
            text = message,
            client = self.client,
            sms_type = 'rebook'
        )

    def getTimeOfDayColor(self):
        if self.timeOfTheDay == 'morning':
            return '#3788d8'
        else:
            return 'green'

    def isAllMyPetScheduled(self):
        appointments = Appointment.objects.filter(client=self.client, isActive=True)
        pets = Pet.objects.filter(client=self.client, isActive=True)
        for pet in pets:
            if pet not in [appointment.pet for appointment in appointments]:
                return False
        return True

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"