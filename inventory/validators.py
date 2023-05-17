from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_manufacturing_and_expiry_date(manufacturing_date, expiry_date):
    if manufacturing_date >= expiry_date:
        raise ValidationError(_("Manufacturing date must be earlier than expiry date"))
