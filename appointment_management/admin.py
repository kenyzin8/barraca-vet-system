from django.contrib import admin
from .models import Appointment
# Register your models here.

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'pet', 'timeOfTheDay', 'date', 'purpose', 'status', 'isActive')
    search_fields = ('client', 'pet', 'timeOfTheDay', 'date', 'purpose', 'status', 'isActive')

admin.site.register(Appointment, AppointmentAdmin)