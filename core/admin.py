from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule
from django_celery_results.models import TaskResult, GroupResult

from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('text', 'date_created', 'content_type', 'object_id', 'content_object')
    
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'client', 'email', 'is_active', 'last_login')
    search_fields = ('username', 'client__first_name', 'client__last_name')

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('user', 'action_flag', 'content_type')
    search_fields = ('object_repr', 'change_message', 'user__username')
    list_display = ('user', '__str__', 'content_type', 'action_time')

    def __str__(self):
        return self.object_repr

    def object_repr(self, obj):
        return escape(obj.object_repr) if obj.object_repr else '-'
    object_repr.short_description = 'Object'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(GroupResult)

LogEntry._meta.verbose_name_plural = 'Log Entries'

#------------------------------------------------------------------------------------
admin.site.site_header = "Barraca Veterinary Clinic - Admin Control Panel"
admin.site.site_title = "Barraca Veterinary Clinic"
admin.site.index_title = "System Admin"
#-------------------------------------------------------------------------------------