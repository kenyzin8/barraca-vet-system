from django import template
from django.contrib.auth.models import Permission

register = template.Library()

@register.filter
def has_permission(user, permission_name):
    return user.has_perm(permission_name)
    
@register.filter
def reverse_list(value):
    return reversed(value)