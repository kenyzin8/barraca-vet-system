from django.contrib.auth.decorators import login_required
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