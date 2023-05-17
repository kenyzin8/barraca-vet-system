from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    service_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'service-type-list'}))
    fee = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    remarks = forms.ChoiceField(choices=Service.REMARKS_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Service
        fields = ['service_type', 'fee', 'remarks']