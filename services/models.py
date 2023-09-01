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

    service_type = models.CharField(max_length=50)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    #remarks = models.CharField(max_length=20, choices=REMARKS_TYPES)
    date_added = models.DateTimeField(auto_now=True)
    control_number = models.CharField(max_length=50, default=1)
    active = models.BooleanField(default=True)
    
    changes_log = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Service.objects.get(pk=self.pk)
            changes = {}

            if orig.service_type != self.service_type:
                changes['service_type'] = [orig.service_type, self.service_type]
            if orig.fee != self.fee:
                changes['fee'] = [str(orig.fee), str(self.fee)]
            if orig.remarks != self.remarks:
                changes['remarks'] = [orig.remarks, self.remarks]
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

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.service_type}"