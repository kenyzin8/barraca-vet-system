from django import forms
from .models import Service
from django.core.exceptions import ValidationError

class ServiceForm(forms.ModelForm):
    service_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'service-type-list', 'placeholder': 'Service name'}))
    fee = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Service fee'}))
    # selection Field
    job_for = forms.ChoiceField(choices=Service.VET_CLINIC_POSITION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    service_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Service description'}))
    #remarks = forms.ChoiceField(choices=Service.REMARKS_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if instance.service_type in ["Check-up", "Deworming", "Vaccination", "Doctor's Fee", "Follow-up Check-up"]:
                self.fields['service_type'].disabled = True
    class Meta:
        model = Service
        fields = ['service_type', 'fee', 'job_for', 'service_description']

    def clean(self):
        price = self.cleaned_data.get('fee')
        str_price = str(price)

        if '.' in str_price and len(str_price.split('.')[1]) > 2:
            raise ValidationError('You can only input 8 digits and 2 decimal points for the fee.')

        if len(str_price.replace('.', '')) > 10:
            raise ValidationError('You can only input 8 digits for the fee.')