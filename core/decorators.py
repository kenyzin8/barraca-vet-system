from django.http import Http404
from functools import wraps

def staff_required(function):
    @wraps(function)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_superuser or request.user.is_staff):
            raise Http404("Page not found")
        return function(request, *args, **kwargs)
    return _wrapped_view
