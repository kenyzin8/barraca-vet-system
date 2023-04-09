from django.contrib import admin
from .models import Client, Pet

class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'contact_number', 'address')
    search_fields = ('first_name', 'last_name', 'user__email')

    def email(self, obj):
        return obj.user.email

    email.short_description = 'Email'

class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'age', 'gender', 'client')
    search_fields = ('name', 'species', 'client__first_name', 'client__last_name')

admin.site.register(Client, ClientAdmin)
admin.site.register(Pet, PetAdmin)

#---------------------------NOT RELATED TO THIS APP-----------------------------------
admin.site.site_header = "Barraca Veterinary Clinic - Admin Control Panel"
admin.site.site_title = "Barraca Veterinary Clinic"
admin.site.index_title = "System Admin"
#-------------------------------------------------------------------------------------