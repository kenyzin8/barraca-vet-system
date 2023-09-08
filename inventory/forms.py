from django import forms
from .models import Product, ProductType
from .validators import validate_manufacturing_and_expiry_date
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    product_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control'}))
    quantity_on_stock = forms.DecimalField(
        widget=forms.NumberInput(attrs={'id': 'quantity', 'class': 'form-control'}),
        decimal_places=2, 
    )
    volume = forms.DecimalField(
        widget=forms.NumberInput(attrs={'id': 'quantity', 'class': 'form-control'}),
        decimal_places=2, 
    )  
    form = forms.ChoiceField(choices=Product.PRODUCT_FORM_LIST, widget=forms.Select(attrs={'id': 'form', 'class': 'form-select'}))
    type = forms.ModelChoiceField(queryset=ProductType.objects.filter(active=True).order_by('-id'), widget=forms.Select(attrs={'id': 'type', 'class': 'form-select'}))
    batch_number = forms.CharField(widget=forms.TextInput(attrs={'id': 'batch_number', 'class': 'form-control', 'list': 'previous-batch-numbers'}))
    manufacturer = forms.CharField(widget=forms.TextInput(attrs={'id': 'manufacturer', 'class': 'form-control'}))
    manufacturing_date = forms.DateField(widget=forms.DateInput(attrs={'id': 'manufacturing_date', 'class': 'form-control', 'type': 'date'}))
    expiration_date = forms.DateField(widget=forms.DateInput(attrs={'id': 'expiration_date', 'class': 'form-control', 'type': 'date'}))
    critical_level = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'critical_level', 'class': 'form-control'}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'id': 'price', 'class': 'form-control'}))
    product_description = forms.CharField(widget=forms.Textarea(attrs={'id': 'product_description', 'class': 'form-control'}))

    class Meta:
        model = Product
        fields = ('product_name', 'quantity_on_stock', 'volume', 'form', 'type', 'batch_number', 'manufacturer', 'manufacturing_date', 'expiration_date', 'critical_level', 'price', 'product_description')

    def clean(self):
        cleaned_data = super().clean()
        manufacturing_date = cleaned_data.get('manufacturing_date')
        expiration_date = cleaned_data.get('expiration_date')
        quantity_on_stock = cleaned_data.get('quantity_on_stock')
        critical_level = cleaned_data.get('critical_level')

        price = self.cleaned_data.get('price')
        str_price = str(price)
        str_quantity_on_stock = str(quantity_on_stock)

        if validate_manufacturing_and_expiry_date(manufacturing_date, expiration_date):
            raise ValidationError(("Manufacturing date must be earlier than expiry date."))

        if '.' in str_price and len(str_price.split('.')[1]) > 2:
            raise ValidationError('You can only input 8 digits and 2 decimal points for the price.')

        if '.' in str_quantity_on_stock and len(str_quantity_on_stock.split('.')[1]) > 2:
            raise ValidationError('Quantity on stock can only have up to 2 decimal points.')

        if len(str_price.replace('.', '')) > 10:
            raise ValidationError('You can only input 8 digits for the price.')

        if critical_level > quantity_on_stock:
            raise ValidationError('Critical level must not be greater than quantity on stock.')
