from django import forms
from .models import Appointment
from record_management.models import Client, Pet
from services.models import Service
from django.db.models import Q

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'pet', 'timeOfTheDay', 'purpose']

    client = forms.ModelChoiceField(
        #filter only clients with pets
        queryset = Client.objects.filter(pet__isnull=False).distinct(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_client'}),  
    )
    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pet'}), 
    )
    purpose = forms.ModelChoiceField(
        #filter only active services and only the name should be displayed
        queryset=Service.objects.filter(active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Service'
    )
    timeOfTheDay = forms.ChoiceField(
        choices=Appointment.time_of_the_day_choices,
        widget=forms.Select(attrs={'class': 'form-select'}), 
        label='Time of the Day'
    )

class RebookAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet', 'purpose', 'timeOfTheDay']

    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pet-rebook', 'name': 'pet-rebook'}), 
    )
    purpose = forms.ModelChoiceField(
        #filter only active services and only the name should be displayed
        queryset=Service.objects.filter(active=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_purpose-rebook'}),
        label='Service'
    )

    timeOfTheDay = forms.ChoiceField(
        choices=Appointment.time_of_the_day_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_timeOfTheDay-rebook'}),
        label='Time of the Day'
    )
