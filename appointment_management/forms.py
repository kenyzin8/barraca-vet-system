from django import forms
from .models import DoctorSchedule, Appointment, DateSlot, MaximumAppointment
from record_management.models import Client, Pet
from services.models import Service
from django.db.models import Q

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'pet', 'purpose', 'time']

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
        queryset=Service.objects.filter(active=True).exclude(service_type__icontains="doctor's fee"),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Service'
    )
    # timeOfTheDay = forms.ChoiceField(
    #     choices=Appointment.time_of_the_day_choices,
    #     widget=forms.Select(attrs={'class': 'form-select'}), 
    #     label='Time of the Day'
    # )

    time = forms.ChoiceField(
        choices=Appointment.time_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Time'
    )

class AppointmentFormClient(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet', 'purpose', 'time']

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
        queryset=Service.objects.filter(active=True).exclude(service_type__icontains="doctor's fee"),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Service'
    )
    time = forms.ChoiceField(
        choices=Appointment.time_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Time'
    )
    # timeOfTheDay = forms.ChoiceField(
    #     choices=Appointment.time_of_the_day_choices,
    #     widget=forms.Select(attrs={'class': 'form-select'}), 
    #     label='Time of the Day'
    # )

class RebookAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet', 'purpose', 'time']

    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pet-rebook', 'name': 'pet-rebook', 'disabled': 'disabled'}), 
    )
    purpose = forms.ModelChoiceField(
        #filter only active services and only the name should be displayed
        queryset=Service.objects.filter(active=True).exclude(service_type__icontains="doctor's fee"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_purpose-rebook'}),
        label='Service'
    )

    # timeOfTheDay = forms.ChoiceField(
    #     choices=Appointment.time_of_the_day_choices,
    #     widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_timeOfTheDay-rebook'}),
    #     label='Time of the Day'
    # )

    time = forms.ChoiceField(
        choices=Appointment.time_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_time-rebook'}),
        label='Time'
    )

class RebookAppointmentFormClient(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet_rebook', 'purpose', 'time']

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
        queryset=Service.objects.filter(active=True).exclude(service_type__icontains="doctor's fee"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_purpose-rebook'}),
        label='Service'
    )
    # timeOfTheDay = forms.ChoiceField(
    #     choices=Appointment.time_of_the_day_choices,
    #     widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_timeOfTheDay-rebook'}),
    #     label='Time of the Day'
    # )
    time = forms.ChoiceField(
        choices=Appointment.time_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_time-rebook'}),
        label='Time'
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
        fields = ['morning_slots', 'afternoon_slots']

    morning_slots = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}), 
        label='Morning Slots'
    )

    afternoon_slots = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}), 
        label='Afternoon Slots'
    )

    def __init__(self, *args, **kwargs):
        super(DateSlotForm, self).__init__(*args, **kwargs)
        max_appointments = MaximumAppointment.load().max_appointments  
        
        self.fields['morning_slots'].widget.attrs['max'] = max_appointments // 2
        self.fields['afternoon_slots'].widget.attrs['max'] = max_appointments // 2

class ChangeTimeForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['time']

    time = forms.ChoiceField(
        choices=Appointment.time_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_time-change'}),
        label='Time'
    )
