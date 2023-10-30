from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_manufacturing_and_expiry_date(manufacturing_date, expiry_date):
    if manufacturing_date >= expiry_date:
        return True

def validate_quantity(value):
    if value < 1:
        raise ValidationError('Invalid quantity.')

def validate_volume(value):
    if value < 1:
        raise ValidationError('Invalid volume.')

def validate_critical(value):
    if value < 1:
        raise ValidationError('Invalid critical.')

def validate_selling(value):
    if value < 1:
        raise ValidationError('Invalid price.')