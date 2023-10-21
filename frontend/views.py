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

from services.models import Service
from inventory.models import Product

# @cache_page(60)
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def pricing(request):
    services = Service.objects.all()
    products = Product.objects.all()

    modified_services = []

    for service in services:
        if service.fee > 0:
            modified_services.append(service)

    modified_products = []

    for product in products:
        if product.price > 0:
            if not product.is_product_expired and not product.is_product_out_of_stock:
                modified_products.append(product)

    context = {'services': modified_services, 'products': products}

    return render(request, 'pricing.html', context)

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