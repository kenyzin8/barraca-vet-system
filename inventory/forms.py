from django import forms
from .models import Product, ProductType
from .validators import validate_manufacturing_and_expiry_date, validate_quantity, validate_volume, validate_selling, validate_critical
from django.core.exceptions import ValidationError
from datetime import date

class ProductForm(forms.ModelForm):
    product_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'name', 'class': 'form-control', 'placeholder': 'Product Name'}))
    quantity_on_stock = forms.DecimalField(
        widget=forms.NumberInput(attrs={'id': 'quantity', 'class': 'form-control', 'min': 1, 'max': 10000,'placeholder': 'Product Quantity'}), 
        validators=[validate_quantity],
    )
    volume = forms.DecimalField(
        widget=forms.NumberInput(attrs={'id': 'volume', 'class': 'form-control', 'min': 1, 'max': 10000, 'placeholder': 'Product Volume'}),
        decimal_places=2, 
        validators=[validate_volume],
    )  
    volume_unit = forms.ChoiceField(choices=Product.VOLUME_UNIT_CHOICES, widget=forms.Select(attrs={'id': 'volume_unit', 'class': 'form-select'}))
    form = forms.ChoiceField(choices=Product.PRODUCT_FORM_LIST, widget=forms.Select(attrs={'id': 'form', 'class': 'form-select'}))
    type = forms.ModelChoiceField(queryset=ProductType.objects.filter(active=True).order_by('-id'), widget=forms.Select(attrs={'id': 'type', 'class': 'form-select'}))
    batch_number = forms.CharField(widget=forms.TextInput(attrs={'id': 'batch_number', 'class': 'form-control', 'list': 'previous-batch-numbers', 'placeholder': 'Product Batch Number'}))
    manufacturer = forms.CharField(widget=forms.TextInput(attrs={'id': 'manufacturer', 'class': 'form-control', 'placeholder': 'Product Manufacturer'}))
    
    today = date.today().strftime('%Y-%m-%d')

    manufacturing_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'id': 'manufacturing_date', 
            'class': 'form-control', 
            'type': 'date',
            'max': today
        })
    )
    expiration_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'id': 'expiration_date', 
            'class': 'form-control', 
            'type': 'date',
            'min': today
        })
    )

    critical_level = forms.IntegerField(validators=[validate_critical], widget=forms.NumberInput(attrs={'id': 'critical_level', 'class': 'form-control', 'min': 1, 'placeholder': 'Product Critical Level'}))
    price = forms.DecimalField(validators=[validate_selling], widget=forms.NumberInput(attrs={'id': 'price', 'class': 'form-control', 'min': 1, 'max': 10000,'placeholder': 'Product Price'}))
    product_description = forms.CharField(widget=forms.Textarea(attrs={'id': 'product_description', 'class': 'form-control', 'placeholder': 'Product Description'}))

    class Meta:
        model = Product
        fields = ('product_name', 'quantity_on_stock', 'volume', 'volume_unit', 'form', 'type', 'batch_number', 'manufacturer', 'manufacturing_date', 'expiration_date', 'critical_level', 'price', 'product_description')

    def clean(self):
        cleaned_data = super().clean()
        manufacturing_date = cleaned_data.get('manufacturing_date')
        expiration_date = cleaned_data.get('expiration_date')
        quantity_on_stock = cleaned_data.get('quantity_on_stock')
        critical_level = cleaned_data.get('critical_level')
        quantity_on_stock = cleaned_data.get('quantity_on_stock')

        price = cleaned_data.get('price')
        str_price = str(price)
        str_quantity_on_stock = str(quantity_on_stock)

        if validate_manufacturing_and_expiry_date(manufacturing_date, expiration_date):
            #raise ValidationError(("Manufacturing date must be earlier than expiry date."))
            self.add_error('manufacturing_date', 'Error: Manufacturing date must be earlier than expiry date.')

        if expiration_date <= date.today():
            self.add_error('expiration_date', 'Error: Expiration date must be later than today.')
            #raise ValidationError('Expiration date must be later than today.')

        if '.' in str_price and len(str_price.split('.')[1]) > 2:
            self.add_error('price', 'Error: Price can only have up to 2 decimal points.')
            #raise ValidationError('You can only input 8 digits and 2 decimal points for the price.')

        if '.' in str_quantity_on_stock and len(str_quantity_on_stock.split('.')[1]) > 2:
            self.add_error('quantity_on_stock', 'Error: Quantity on stock can only have up to 2 decimal points.')
            #raise ValidationError('Quantity on stock can only have up to 2 decimal points.')

        if price > 10000:
            self.add_error('price', 'Error: Price must not be greater than ₱10,000.00')
            #raise ValidationError('Price must not be greater than ₱10,000.00')

        if len(str_price.replace('.', '')) > 10:
            self.add_error('price', 'Error: You can only input 8 digits for the price.')
            #raise ValidationError('You can only input 8 digits for the price.')

        if critical_level > quantity_on_stock:
            self.add_error('critical_level', 'Error: Critical level must not be greater than quantity on stock.')
            #raise ValidationError('Critical level must not be greater than quantity on stock.')

        if quantity_on_stock > 10000:
            self.add_error('quantity_on_stock', 'Error: Quantity on stock must not be greater than 10,000.')
            #raise ValidationError('Quantity on stock must not be greater than 10,000.')