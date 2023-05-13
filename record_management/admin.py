from django.contrib import admin
from .models import Client, Pet

class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'gender', 'contact_number', 'address', 'two_auth_enabled')
    search_fields = ('first_name', 'last_name', 'gender', 'user__email')

    def email(self, obj):
        return obj.user.email

    email.short_description = 'Email'

class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthday', 'breed', 'gender', 'color', 'weight', 'picture', 'species')
    search_fields = ('name', 'species', 'client__first_name', 'client__last_name')


admin.site.register(Client, ClientAdmin)
admin.site.register(Pet, PetAdmin)