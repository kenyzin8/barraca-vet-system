from django.core.exceptions import ValidationError

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