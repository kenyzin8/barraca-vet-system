from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from django.http import JsonResponse

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        wait = exc.wait
        return JsonResponse({'message': 'Too many requests, please try again later.', 'wait': wait}, status=429)

    return response
