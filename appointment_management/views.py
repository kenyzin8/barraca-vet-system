from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from record_management.models import Client
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page
from django.conf import settings
from datetime import datetime
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from core.semaphore import send_sms, send_otp_sms
from django.contrib.auth.models import User

import json
import requests
import time

@login_required
def calendar(request):
    clients_list = Client.objects.all().order_by('id')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {'clients': []}
        for client in clients_list:
            data['clients'].append({
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'address': client.address,
                'contact_number': client.contact_number,
            })
        return JsonResponse(data)

    context = {
        'clients': clients_list,
        'total_clients': clients_list.count(),
    }

    return render(request, 'calendar.html', context)

@csrf_exempt
@login_required
def send_sms_to_client(request):
    if request.method == 'POST':
        client_ids = json.loads(request.POST.get('client_ids'))
        message = "Welcome to Barraca Veterinary Clinic!"
        contact_numbers = []

        if(type(client_ids) is list):
            for client_id in client_ids:
                try:
                    client = Client.objects.get(id=client_id)
                    contact_numbers.append(client.contact_number)
                except Client.DoesNotExist:
                    pass
        else:
            try:
                client = Client.objects.get(id=client_ids)
                contact_numbers.append(client.contact_number)
            except Client.DoesNotExist:
                pass

        if contact_numbers:
            recipients = ','.join(contact_numbers)
            send_sms(recipients, message)
            return JsonResponse({"status": "success", "message": "SMS sent successfully"})
        else:
            return JsonResponse({"status": "error", "message": "No clients found"})