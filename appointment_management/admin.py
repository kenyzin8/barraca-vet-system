from django.contrib import admin
from .models import Appointment, DoctorSchedule
# Register your models here.

class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason', 'isActive', 'timeOfTheDay')
    search_fields = ('date', 'reason', 'isActive', 'timeOfTheDay')

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'pet', 'timeOfTheDay', 'date', 'purpose', 'status', 'isActive', 'weekly_reminder_sent', 'daily_reminder_sent')
    search_fields = ('client', 'pet', 'timeOfTheDay', 'date', 'purpose', 'status', 'isActive')

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(DoctorSchedule, DoctorScheduleAdmin)