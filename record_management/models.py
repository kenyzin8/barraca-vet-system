from django.db import models
from django.contrib.auth.models import User
from datetime import date
import datetime
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup
from django.apps import apps

class User(AuthUser):
    class Meta:
        proxy = True

class Group(AuthGroup):
    class Meta:
        proxy = True
        
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default="None")
    street = models.CharField(max_length=200, default="None")
    barangay = models.CharField(max_length=200, default="None")
    city = models.CharField(max_length=200, default="None")
    province = models.CharField(max_length=200, default="None")
    contact_number = models.CharField(max_length=15)
    two_auth_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_image(self):
        male_img = 'plugins/sb-admin/assets/img/illustrations/profiles/profile-5.png'
        female_img = 'plugins/sb-admin/assets/img/illustrations/profiles/profile-1.png'

        if self.gender == 'Male':
            return male_img
        elif self.gender == 'Female':
            return female_img

    def get_address(self):
        return f"{self.street}, {self.barangay}, {self.city}, {self.province}"

    class Meta:
        verbose_name_plural = "Clients"

class Pet(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    birthday = models.DateField()
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    color = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    picture = models.ImageField(upload_to='public/images/')
    is_active = models.BooleanField(default=True)
    
    original_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.species})"

    def age(self):
        today = date.today()
        years = today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        months = (today.year - self.birthday.year) * 12 + today.month - self.birthday.month - (today.day < self.birthday.day)
        days = (today - self.birthday).days

        if years > 0:
            age_string = f"{years} year{'s' if years > 1 else ''} old"
        elif months > 0:
            age_string = f"{months} month{'s' if months > 1 else ''} old"
        else:
            age_string = f"{days} day{'s' if days > 1 else ''} old"

        return age_string

    class Meta:
        verbose_name_plural = "Pets"

def validate_image_extension(value):
    import os
    ext = os.path.splitext(value.name)[1] 
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Only PNG and JPG files are allowed.'))

class PetTreatment(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    treatment_date = models.DateTimeField(auto_now=True)
    lab_results = models.CharField(max_length=100, null=True, blank=True)
    treatment_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    diagnosis = models.CharField(max_length=100, null=True, blank=True)
    treatment = models.CharField(max_length=100, null=True, blank=True)
    appointment = models.OneToOneField('appointment_management.Appointment', on_delete=models.CASCADE, null=True, blank=True)
    medical_images = models.ImageField(upload_to='public/images/', null=True, blank=True, default='None', validators=[validate_image_extension])
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pet.name} - {self.treatment}"

    def get_owner(self):
        return self.pet.client.full_name

    class Meta:
        verbose_name_plural = "Pet Treatments"

class PetMedicalPrescription(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    medicines = models.ManyToManyField('inventory.Product', through='PrescriptionMedicines')
    date_prescribed = models.DateTimeField(auto_now=True)
    pet_treatment = models.OneToOneField(PetTreatment, on_delete=models.CASCADE, null=True, blank=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pet.name} - {self.date_prescribed}"

    class Meta:
        verbose_name_plural = "Pet Medical Prescriptions"

class PrescriptionMedicines(models.Model):
    """
    PRESCRIPTION DETAILS
    """

    MEDICINES_FORM_LIST = (
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
    )

    prescription = models.ForeignKey(PetMedicalPrescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='prescription_medicines', null=True)
    strength = models.CharField(max_length=100)
    form = models.CharField(max_length=20, choices=MEDICINES_FORM_LIST)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    remarks = models.CharField(max_length=100)

    #extra attributes if medicine is not around on the inventory
    extra_medicine = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.prescription.pet.name} - {self.medicine.product_name}"

    class Meta:
        verbose_name_plural = "Prescription Medicines"


# DEPRECATED: This model is no longer in active use but is preserved for data integrity.
class PetHealthCard(models.Model):

    TREATMENTS_LIST = (
        ('deworming', 'Deworming'),
        ('vaccination', 'Vaccination'),
    )

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    visit_date = models.DateTimeField(auto_now=True)
    next_treatment = models.OneToOneField('appointment_management.Appointment', on_delete=models.CASCADE)
    treatment = models.CharField(max_length=20, choices=TREATMENTS_LIST)
    medicine_used = models.CharField(max_length=100)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pet.name} - {self.treatment} - {self.visit_date} - {self.next_treatment.date}"
    
    class Meta:
        verbose_name_plural = "Pet Health Cards"

class PetMedicalRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    visit_date = models.DateTimeField(auto_now=True)
    lab_results = models.CharField(max_length=100, null=True, blank=True)
    findings = models.CharField(max_length=100, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    diagnosis = models.CharField(max_length=100, null=True, blank=True)
    treatment = models.CharField(max_length=100, null=True, blank=True)
    medical_images = models.ImageField(upload_to='public/images/', null=True, blank=True)
    isActive = models.BooleanField(default=True)
    prescription = models.OneToOneField(PetMedicalPrescription, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pet.name} - {self.visit_date}"

    class Meta:
        verbose_name_plural = "Pet Medical Records"