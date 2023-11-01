from django.contrib import admin
from .models import Appointment, DoctorSchedule, MaximumAppointment, DateSlot, SMSTemplate
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
from .forms import SMSTemplateForm

class SMSTemplateAdmin(admin.ModelAdmin):
    form = SMSTemplateForm
    list_display = ('id', 'name', 'template')
    search_fields = ('name', 'template')

class DateSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'morning_slots', 'afternoon_slots', 'isActive')
    search_fields = ('date','isActive')

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
    list_display = ('id', 'client', 'pet', 'time', 'date', 'purpose', 'status', 'isActive', 'weekly_reminder_sent', 'daily_reminder_sent')
    search_fields = ('client', 'pet', 'time', 'date', 'purpose', 'status', 'isActive')
    actions = ['set_as_pending', 'set_as_cancelled', 'set_as_done', 'set_as_rebook']

    def log_change(self, request, queryset, action, status):
        rows_updated = queryset.update(status=status, isActive=action)
        if rows_updated:
            for obj in queryset:
                message = f'Appointment {obj.id} status set to {status} and active set to {action}.'
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(obj).pk,
                    object_id=obj.pk,
                    object_repr=force_str(obj),
                    action_flag=CHANGE,
                    change_message=message,
                )

    def set_as_pending(self, request, queryset):
        self.log_change(request, queryset, True, 'pending')

    def set_as_cancelled(self, request, queryset):
        self.log_change(request, queryset, False, 'cancelled')

    def set_as_done(self, request, queryset):
        self.log_change(request, queryset, False, 'done')

    def set_as_rebook(self, request, queryset):
        self.log_change(request, queryset, True, 'rebook')

    set_as_pending.short_description = "Set selected appointments as pending"
    set_as_cancelled.short_description = "Set selected appointments as cancelled"
    set_as_done.short_description = "Set selected appointments as done"
    set_as_rebook.short_description = "Set selected appointments as rebook"

admin.site.register(SMSTemplate, SMSTemplateAdmin)
admin.site.register(DateSlot, DateSlotAdmin)
admin.site.register(MaximumAppointment, MaximumAppointmentAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(DoctorSchedule, DoctorScheduleAdmin)