from django.contrib import admin
from .models import Client, Pet
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin, GroupAdmin as AuthGroupAdmin
from .models import User, Group, PetTreatment, PetMedicalPrescription, PrescriptionMedicines

class PetTreatmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'treatment_date', 'lab_results', 'treatment_weight', 'temperature', 'diagnosis', 'treatment', 'appointment', 'isActive')
    list_filter = ('pet__name', 'pet__species', 'pet__breed', 'treatment_date', 'isActive')
    search_fields = ('pet__name', 'pet__species', 'pet__breed', 'treatment_date', 'isActive')
    
class PrescriptionMedicines(admin.TabularInline):
    model = PrescriptionMedicines
    extra = 1

class PetMedicalPrescriptionAdmin(admin.ModelAdmin):
    inlines = (PrescriptionMedicines,)
    list_display = ('pet', 'date_prescribed', 'isActive')
    list_filter = ('pet__name', 'pet__species', 'pet__breed', 'date_prescribed', 'isActive')
    search_fields = ('pet__name', 'pet__species', 'pet__breed', 'date_prescribed', 'isActive')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'gender', 'contact_number', 'street', 'barangay', 'city', 'province', 'two_auth_enabled')
    search_fields = ('first_name', 'last_name', 'gender', 'user__email')

    def email(self, obj):
        return obj.user.email

    email.short_description = 'Email'

class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthday', 'breed', 'gender', 'color', 'weight', 'picture', 'species', 'is_active')
    search_fields = ('name', 'species', 'client__first_name', 'client__last_name')

admin.site.register(PetTreatment, PetTreatmentAdmin)
admin.site.register(PetMedicalPrescription, PetMedicalPrescriptionAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Pet, PetAdmin)

admin.site.register(User, AuthUserAdmin)
admin.site.register(Group, AuthGroupAdmin)

# class PetMedicalRecordAdmin(admin.ModelAdmin):
#     list_display = ('pet', 'visit_date', 'isActive')
#     list_filter = ('pet__name', 'pet__species', 'pet__breed', 'visit_date', 'isActive')
#     search_fields = ('pet__name', 'pet__species', 'pet__breed', 'visit_date', 'isActive')

# class PetHealthCardAdmin(admin.ModelAdmin):
#     list_display = ('pet', 'visit_date', 'next_treatment', 'treatment', 'medicine_used', 'isActive')
#     list_filter = ('pet__name', 'pet__species', 'pet__breed', 'visit_date', 'isActive')
#     search_fields = ('pet__name', 'pet__species', 'pet__breed', 'visit_date', 'isActive')


# admin.site.register(PetHealthCard, PetHealthCardAdmin)
# admin.site.register(PetMedicalRecord, PetMedicalRecordAdmin)