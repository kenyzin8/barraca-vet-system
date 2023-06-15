from django.db import models

# Create your models here.
class Service(models.Model):
    SERVICE_TYPES = (
        ('deworming', 'Deworming'),
        ('vaccination', 'Vaccination'),
        ('checkup', 'Check-up'),
        ('procedure', 'Procedure'),
        ('other', 'Other'),
    )

    REMARKS_TYPES = (
        ('without_medicine', 'Without Medicine'),
        ('with_medicine', 'With Medicine'),
    )

    service_type = models.CharField(max_length=50)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.CharField(max_length=20, choices=REMARKS_TYPES)
    date_added = models.DateTimeField(auto_now=True)
    control_number = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    previous_version = models.TextField(blank=True, null=True)  
    updated_version = models.TextField(blank=True, null=True) 
    original_service_type = models.CharField(max_length=50, null=True)
    
    def create_new_version(self, new_service_type=None, new_fee=None, new_remarks=None):
        previous_version = None
        updated_version = None

        if new_service_type and new_service_type != self.service_type:
            previous_version = f"Service Type: {self.service_type}"
            updated_version = f"Service Type: {new_service_type}"
            service_type = new_service_type
        else:
            service_type = self.service_type

        if new_fee and new_fee != self.fee:
            previous_version = f"Fee: ₱ {self.fee}"
            updated_version = f"Fee: ₱ {new_fee}"
            fee = new_fee
        else:
            fee = self.fee

        if new_remarks and new_remarks != self.remarks:
            previous_version = f"Remarks: {self.remarks}"
            updated_version = f"Remarks: {new_remarks}"
            remarks = new_remarks
        else:
            remarks = self.remarks

        self.active = False
        self.save()

        new_service = Service.objects.create(
            service_type=service_type,
            original_service_type=self.original_service_type,
            fee=fee,
            remarks=remarks,
            control_number=self.control_number + 1,
            active=True,
            previous_version=previous_version,
            updated_version=updated_version
        )

        return new_service

    def __str__(self):
        return f"{self.service_type} - {self.fee}"