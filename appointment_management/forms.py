from django import forms
from .models import DoctorSchedule, Appointment, DateSlot, MaximumAppointment
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

class AppointmentFormClient(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet', 'timeOfTheDay', 'purpose']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(AppointmentFormClient, self).__init__(*args, **kwargs)
        if request:
            pets_with_appointments = Appointment.objects.exclude(status__in=['cancelled', 'done']).filter(pet__client=request.user.client, isActive=True).values_list('pet', flat=True)
            self.fields['pet'].queryset = Pet.objects.filter(client=request.user.client, is_active=True).exclude(id__in=pets_with_appointments)

    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pet'}), 
    )
    purpose = forms.ModelChoiceField(
        # filter only active services and only the name should be displayed
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
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pet-rebook', 'name': 'pet-rebook', 'disabled': 'disabled'}), 
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

class RebookAppointmentFormClient(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet_rebook', 'purpose', 'timeOfTheDay']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(RebookAppointmentFormClient, self).__init__(*args, **kwargs)
        if request:
            pets_with_appointments = Appointment.objects.exclude(status__in=['cancelled', 'done']).filter(pet__client=request.user.client).values_list('pet', flat=True)
            self.fields['pet_rebook'].queryset = Pet.objects.filter(client=request.user.client).exclude(id__in=pets_with_appointments)
            
    pet_rebook = forms.ModelChoiceField(
        queryset=Pet.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pet-rebook', 'name': 'pet-rebook', 'disabled': 'disabled'}), 
        label="Pet"
    )
    purpose = forms.ModelChoiceField(
        queryset=Service.objects.filter(active=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_purpose-rebook'}),
        label='Service'
    )
    timeOfTheDay = forms.ChoiceField(
        choices=Appointment.time_of_the_day_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_timeOfTheDay-rebook'}),
        label='Time of the Day'
    )

class DisableDayForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ['reason', 'timeOfTheDay']

    reason = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Reason')
    
    timeOfTheDay = forms.ChoiceField(
        choices=DoctorSchedule.time_of_the_day_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_timeOfTheDay-disable'}),
        label='Time of the Day'
    )

class DateSlotForm(forms.ModelForm):
    class Meta:
        model = DateSlot
        fields = ['slots']

    slots = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}), 
        label='Slots'
    )

    def __init__(self, *args, **kwargs):
        super(DateSlotForm, self).__init__(*args, **kwargs)
        max_appointments = MaximumAppointment.load().max_appointments  
        self.fields['slots'].widget.attrs['max'] = max_appointments 

class ChangeTimeForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['timeOfTheDay']

    timeOfTheDay = forms.ChoiceField(
        choices=Appointment.time_of_the_day_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_timeOfTheDay-change'}),
        label='Time of the Day'
    )