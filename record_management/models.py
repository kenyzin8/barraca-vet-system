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
    isBanned = models.BooleanField(default=False)
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
    symptoms = models.CharField(max_length=100, null=True, blank=True)
    treatment_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    diagnosis = models.CharField(max_length=100, null=True, blank=True)
    treatment = models.CharField(max_length=100, null=True, blank=True)
    appointment = models.OneToOneField('appointment_management.Appointment', on_delete=models.CASCADE, null=True, blank=True)
   
    #medical_images = models.ImageField(upload_to='public/images/', null=True, blank=True, default='None', validators=[validate_image_extension])
    lab_results = models.ManyToManyField('record_management.LabResult', blank=True)

    isHealthCard = models.BooleanField(default=False)

    isActive = models.BooleanField(default=True)
    isVaccine = models.BooleanField(default=False)
    isDeworm = models.BooleanField(default=False)

    hasMultipleCycles = models.BooleanField(default=False)
    appointment_cycles = models.JSONField(blank=True, null=True)  
    cycles_remaining = models.PositiveIntegerField(default=0)  

    def __str__(self):
        return f"{self.pet.name} - {self.treatment}"

    def get_owner(self):
        return self.pet.client.full_name

    def get_lab_result_image_for_health_card(self):
        try:
            image = self.lab_results.first().result_image
            if image:
                return image
            else:
                return None
        except:
            return None
    class Meta:
        verbose_name_plural = "Pet Treatments"

class LabResult(models.Model):
    result_name = models.CharField(max_length=100, null=True, blank=True)
    result_image = models.ImageField(upload_to='public/images/', null=True, blank=True, default='None', validators=[validate_image_extension])

    isActive = models.BooleanField(default=True)

    def is_image(self):
        return self.result_image != 'None'

    def __str__(self):
        return self.result_name

    class Meta:
        verbose_name_plural = "Lab Results"

class TemporaryLabResultImage(models.Model):
    image = models.ImageField(upload_to='public/images/', validators=[validate_image_extension])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Temporary Lab Result Images"

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
    strength = models.CharField(max_length=100, null=True, blank=True)
    #form = models.CharField(max_length=20, choices=MEDICINES_FORM_LIST) DEPRECIATED
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dosage = models.CharField(max_length=100, null=True, blank=True)
    frequency = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.CharField(max_length=100, null=True, blank=True)

    #extra attributes if medicine is not around on the inventory
    extra_medicine = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.prescription.pet.name} - {self.medicine.product_name}"

    def get_medicine_name(self):
        return self.medicine.product_name
    
    def get_prescription_details(self):
        self.remarks = self.remarks[0].lower() + self.remarks[1:]
        self.frequency = self.frequency[0].lower() + self.frequency[1:]

        prescription_details = f"Prescribed: {self.quantity} of {self.medicine.product_name} ({self.strength} per {self.get_dosage_unit()}). "

        prescription_details += f"Dosage: Administer {self.dosage} {self.get_dosage_unit()} to the pet {self.frequency}. "

        prescription_details += f"For best results or safety, it's recommended to {self.remarks}."

        return prescription_details

    def get_dosage_unit(self, for_dosage=False):
        liquid_forms = ['syrup', 'liquid', 'oral_solution', 'suspension', 'ear_drop', 'gel', 'cream', 'ointment', 'lotion']
        
        if self.medicine.form in liquid_forms:
            return 'mL'
        else:
            if for_dosage and self.dosage != '1':
                return self.medicine.form + 's'
            return self.medicine.form

    def get_quantity_description(self):
        solid_forms_with_plural = {
            'tablet': 'tablet',
            'capsule': 'capsule',
            'granule': 'granule',
            'chew': 'chewable',
            'pellet': 'pellet',
            'powder': 'powder',
            'bolus': 'bolus',
            'paste': 'paste'  # added
        }

        liquid_forms = {
            'syrup': 'ml',
            'liquid': 'ml',
            'oral_solution': 'ml',
            'ear_drop': 'ml',
            'gel': 'ml',
            'cream': 'ml',
            'ointment': 'ml',
            'lotion': 'ml',
            'suspension': 'ml',
            'feed_additive': 'ml',  
            'drop': 'ml', 
            'spray': 'ml'  
        }


        other_forms = {
            'injection': 'dose', 
            'spot-on': 'dose', 
            'other': 'unit' 
        }

        if self.medicine.form in solid_forms_with_plural:
            unit = solid_forms_with_plural[self.medicine.form]
            return f"{self.quantity} {unit}{'s' if self.quantity > 1 else ''}"
        elif self.medicine.form in liquid_forms:
            return f"- {self.medicine.volume} {liquid_forms[self.medicine.form]}"
        elif self.medicine.form in other_forms:
            return f"- {self.quantity} {other_forms[self.medicine.form]}"
        else:
            return ""
        
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

class LabResultsTreatment(models.Model):
    pet_treatment = models.OneToOneField(PetTreatment, on_delete=models.CASCADE, null=True, blank=True)
    lab_result = models.ForeignKey('record_management.LabResult', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.pet_treatment.pet.name} - {self.lab_result.result_name}"

class TreatmentCycle(models.Model):
    pet_treatment = models.ForeignKey(PetTreatment, on_delete=models.CASCADE, related_name="cycles")
    appointment = models.ForeignKey('appointment_management.Appointment', on_delete=models.CASCADE)
    cycle_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ['pet_treatment', 'cycle_number']
        verbose_name_plural = "Pet Treatment Cycles"