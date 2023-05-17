from django import forms
from .models import Product
from .validators import validate_manufacturing_and_expiry_date
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    product_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control'}))
    quantity_on_stock = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'quantity', 'class': 'form-control'}))
    type = forms.ChoiceField(choices=Product.TYPES, widget=forms.Select(attrs={'id': 'type', 'class': 'form-select'}))
    batch_number = forms.CharField(widget=forms.TextInput(attrs={'id': 'batch_number', 'class': 'form-control', 'list': 'previous-batch-numbers'}))
    manufacturing_date = forms.DateField(widget=forms.DateInput(attrs={'id': 'manufacturing_date', 'class': 'form-control', 'type': 'date'}))
    expiration_date = forms.DateField(widget=forms.DateInput(attrs={'id': 'expiration_date', 'class': 'form-control', 'type': 'date'}))
    critical_level = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'critical_level', 'class': 'form-control'}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'id': 'price', 'class': 'form-control'}))

    class Meta:
        model = Product
        fields = ('product_name', 'quantity_on_stock', 'type', 'batch_number', 'manufacturing_date', 'expiration_date', 'critical_level', 'price')

    def clean(self):
        cleaned_data = super().clean()
        manufacturing_date = cleaned_data.get('manufacturing_date')
        expiration_date = cleaned_data.get('expiration_date')

        if validate_manufacturing_and_expiry_date(manufacturing_date, expiration_date):
            raise ValidationError(("Manufacturing date must be earlier than expiry date."))

        price = self.cleaned_data.get('price')
        str_price = str(price)

        if '.' in str_price and len(str_price.split('.')[1]) > 2:
            raise ValidationError('You can only input 8 digits and 2 decimal points for the price.')

        if len(str_price.replace('.', '')) > 10:
            raise ValidationError('You can only input 8 digits for the price.')

        quantity_on_stock = cleaned_data.get('quantity_on_stock')
        critical_level = cleaned_data.get('critical_level')

        if critical_level > quantity_on_stock:
            raise ValidationError('Critical level must not be greater than quantity on stock.')