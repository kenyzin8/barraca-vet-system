from django.core.exceptions import ValidationError
import re

def validate_phone_number(value):
    if len(value) != 11 or not value.startswith("09"):
        raise ValidationError("Phone number must start with '09' and be 11 digits long.",
                              params={'field_display': 'Contact Number'})

def validate_image_size(image):
    file_size = image.size
    limit_mb = 2
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError("Max size of file is %s MB." % limit_mb,
                              params={'field_display': 'Picture'})

def validate_weight(value):
    if value < 1 or value > 150:
        raise ValidationError('Weight should be between 1kg and 150kg.')

def validate_contains_special_character(value):
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('The password must contain at least one special character. (e.g., @, #, $, etc.)')

def validate_contains_digit(value):
    if not re.search(r'\d', value):
        raise ValidationError('The password must contain at least one numerical digit.')

def validate_contains_uppercase(value):
    if not re.search(r'[A-Z]', value):
        raise ValidationError('The password must contain at least one uppercase character.')

def validate_first_name(value):
    if re.search(r'[^a-zA-Z\s]', value):
        raise ValidationError('First name should not contain numbers or special characters.')

def validate_last_name(value):
    if re.search(r'[^a-zA-Z\s]', value):
        raise ValidationError('Last name should not contain numbers or special characters.')
