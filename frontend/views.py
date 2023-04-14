from django.shortcuts import render, redirect
from record_management.models import Client
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.conf import settings
from datetime import datetime
from functools import wraps

import requests
import time

# @cache_page(60)
def home(request):
    if request.user.is_authenticated and not hasattr(request.user, 'client'):
        return redirect('register-client-page')

    clients_list = Client.objects.all().order_by('id')
    paginator = Paginator(clients_list, 5)
    page = request.GET.get('page')
    clients = paginator.get_page(page)

    #api_key = settings.SEMAPHORE_API_KEY  # Replace this with your actual API key
    #credit_balance = get_credit_balance(api_key)

    # if credit_balance is None:
    #     message_balance = "The timer hasn't expired. Please wait."
    # else:
    #     message_balance = f"Credit Balance: {credit_balance}"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {'clients': []}
        for client in clients:
            data['clients'].append({
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'address': client.address,
                'contact_number': client.contact_number,
            })
        return JsonResponse(data)

    context = {
        'clients': clients,
        'total_clients': clients_list.count(),
        'clients_per_page': 5
        #"message_balance": message_balance
    }

    return render(request, 'home.html', context)

# def timer(duration):
#     def decorator(func):
#         last_called = [0]

#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             nonlocal last_called
#             current_time = time.time()

#             if current_time - last_called[0] >= duration:
#                 last_called[0] = current_time
#                 print("Current time:", datetime.now())  
#                 return func(*args, **kwargs)
#             else:
#                 time_left = duration - (current_time - last_called[0])
#                 print("Current time:", datetime.now()) 
#                 print(f"Time left until the timer expires: {time_left:.2f} seconds")
#                 return None

#         return wrapper

#     return decorator

# @timer(60)
# def get_credit_balance(api_key):
#     url = "https://api.semaphore.co/api/v4/account"
#     params = {"apikey": api_key}
#     response = requests.get(url, params=params)
#     return response.json()["credit_balance"]

def handler404(request, *args, **argv):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

    