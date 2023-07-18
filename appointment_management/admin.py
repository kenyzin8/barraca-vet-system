from django.contrib import admin
from .models import Appointment, DoctorSchedule, MaximumAppointment, DateSlot
# Register your models here.

class DateSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'slots', 'isActive')
    search_fields = ('date', 'slots', 'isActive')

class MaximumAppointmentAdmin(admin.ModelAdmin):
    list_display = ('max_appointments',)
    search_fields = ('max_appointments',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason', 'isActive', 'timeOfTheDay')
    search_fields = ('date', 'reason', 'isActive', 'timeOfTheDay')

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'pet', 'timeOfTheDay', 'date', 'purpose', 'status', 'isActive', 'weekly_reminder_sent', 'daily_reminder_sent')
    search_fields = ('client', 'pet', 'timeOfTheDay', 'date', 'purpose', 'status', 'isActive')

admin.site.register(DateSlot, DateSlotAdmin)
admin.site.register(MaximumAppointment, MaximumAppointmentAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(DoctorSchedule, DoctorScheduleAdmin)