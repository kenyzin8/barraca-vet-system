from django import forms
from .models import Service
from django.core.exceptions import ValidationError

class ServiceForm(forms.ModelForm):
    service_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'service-type-list'}))
    fee = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    service_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    #remarks = forms.ChoiceField(choices=Service.REMARKS_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Service
        fields = ['service_type', 'fee', 'service_description']

    def clean(self):
        price = self.cleaned_data.get('fee')
        str_price = str(price)

        if '.' in str_price and len(str_price.split('.')[1]) > 2:
            raise ValidationError('You can only input 8 digits and 2 decimal points for the fee.')

        if len(str_price.replace('.', '')) > 10:
            raise ValidationError('You can only input 8 digits for the fee.')