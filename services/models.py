from django.db import models

import datetime

# class ServiceRemarks(models.Model):
#     remarks = models.CharField(max_length=20)
#     active = models.BooleanField(default=True)
#     def __str__(self):
#         return f"{self.remarks}"

#     @classmethod
#     def load(cls):
#         obj, created = cls.objects.get_or_create(pk=1, remarks='without_medicine')
#         obj, created = cls.objects.get_or_create(pk=2, remarks='with_medicine')
#         return obj

#     class Meta:
#         verbose_name = "Service Remark"
#         verbose_name_plural = "Service Remarks"

class Service(models.Model):
    SERVICE_TYPES = (
        ('deworming', 'Deworming'),
        ('vaccination', 'Vaccination'),
        ('checkup', 'Check-up'),
        ('procedure', 'Procedure'),
        ('other', 'Other'),
    )

    list_built_in_services = ['Check-up', 'Deworming', 'Vaccination', 'Doctor\'s Fee', 'Follow-up Check-up']

    service_type = models.CharField(max_length=50)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    #remarks = models.CharField(max_length=20, choices=REMARKS_TYPES)
    date_added = models.DateTimeField(auto_now=True)
    control_number = models.CharField(max_length=50, default=1) #DEPRECIATED
    service_description = models.TextField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    
    changes_log = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Service.objects.get(pk=self.pk)

            if orig.service_type in self.list_built_in_services:
                if orig.service_type != self.service_type:
                    raise ValueError(f"Cannot change the name of the '{orig.service_type}' service.")
                if orig.active != self.active:
                    raise ValueError(f"Cannot change the active status of the '{orig.service_type}' service.")

            changes = {}

            if orig.service_type != self.service_type:
                changes['service_type'] = [orig.service_type, self.service_type]
            if orig.fee != self.fee:
                changes['fee'] = [str(orig.fee), str(self.fee)]
            if orig.service_description != self.service_description:
               changes['service_description'] = [orig.service_description, self.service_description]
            if orig.control_number != self.control_number:
                changes['control_number'] = [str(orig.control_number), str(self.control_number)]
            if orig.active != self.active:
                changes['active'] = [orig.active, self.active]
            
            if changes:
                if self.changes_log:
                    update_id = self.changes_log[-1].get('update_id', 0) + 1
                else:
                    update_id = 1
                
                changes['update_id'] = update_id
                changes['date'] = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")

                if self.changes_log:
                    self.changes_log.append(changes)
                else:
                    self.changes_log = [changes]
        else:
            self.service_type = ' '.join([word.capitalize() for word in self.service_type.split()])

            if self.service_type in self.list_built_in_services:
                existing_service = Service.objects.filter(service_type__iexact=self.service_type, active=True).first()
                if existing_service:
                    raise ValueError(f"'{self.service_type}' service already exists and is active.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.service_type in self.list_built_in_services:
            raise ValueError(f"Cannot delete the '{self.service_type}' service.")
        super(Service, self).delete(*args, **kwargs)

    @classmethod
    def ensure_services_exists(cls):
        services = [
            {"type": "Check-up", "fee": 500.00},
            {"type": "Deworming", "fee": 300.00},  
            {"type": "Vaccination", "fee": 600.00},
            {"type": "Doctor's Fee", "fee": 500.00},
            {"type": "Follow-up Check-up", "fee": 0.00},
        ]
        
        for service in services:
            service_object, created = cls.objects.get_or_create(service_type=service["type"], active=True, defaults={
                'fee': service["fee"],
                'active': True
            })

            if created:
                print(f"Created default '{service['type']}' service.")

    def __str__(self):
        return f"{self.service_type}"