from django.core.exceptions import ValidationError

def validate_phone_number(value):
    if len(value) != 11 or not value.startswith("09"):
        raise ValidationError("Phone number must start with '09' and be 11 digits long.",
                              params={'field_display': 'Contact Number'})