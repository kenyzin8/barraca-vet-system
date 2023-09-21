from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class AdminDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_dashboard'

    def ready(self):
        post_migrate.connect(self.set_up_groups, sender=self)

    @classmethod
    def set_up_groups(cls, **kwargs):
        from django.contrib.auth.models import Group, Permission

        secretary_permissions_codenames = [
            "add_appointment", "change_appointment", "delete_appointment", "view_appointment",
            "add_dateslot", "change_dateslot", "delete_dateslot", "view_dateslot",
            "add_doctorschedule", "change_doctorschedule", "delete_doctorschedule", "view_doctorschedule",
            "add_maximumappointment", "change_maximumappointment", "delete_maximumappointment", "view_maximumappointment",
            "add_user", "view_user",
            "add_billing", "view_billing",
            "add_billingproduct", "view_billingproduct",
            "add_billingservice", "view_billingservice",
            "add_smslogs", "change_smslogs", "delete_smslogs", "view_smslogs",
            "add_client", "view_client",
            "view_labresult", "view_labresultstreatment",
            "add_pet", "view_pet",
            "view_pethealthcard",
            "view_petmedicalprescription",
            "view_petmedicalrecord",
            "view_pettreatment",
            "view_prescriptionmedicines",
            "view_temporarylabresultimage",
            "view_treatmentcycle",
            "add_user", "view_user"
        ]

        secretary_group, created = Group.objects.get_or_create(name="Secretary")
        if created:
            secretary_permissions = Permission.objects.filter(codename__in=secretary_permissions_codenames)
            secretary_group.permissions.set(secretary_permissions)

        doctor_group, _ = Group.objects.get_or_create(name="Doctor")
        doctor_group.permissions.set(Permission.objects.all())