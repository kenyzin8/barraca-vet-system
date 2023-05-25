from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from core.semaphore import fetch_sms_data
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404

from core.decorators import staff_required

import urllib.parse
import requests

from django.contrib.auth.models import User

@login_required
@staff_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
@staff_required
def user_list(request):
    users = User.objects.exclude(client__last_name__icontains='(walk-in)').order_by('-id')
    context = {"users": users}
    return render(request, 'user_management.html', context)

@login_required
@staff_required
def sms_history(request):
    raw_sms_data = fetch_sms_data()

    if isinstance(raw_sms_data, str):
        message = raw_sms_data
        sms_data = None
    else:
        message = None
        sms_data = []
        for sms in raw_sms_data:
            formatted_date_sent = datetime.strptime(sms['created_at'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y - %I:%M %p")
            sms['created_at'] = formatted_date_sent
            sms_data.append(sms)

        sms_data.sort(key=lambda x: x['created_at'], reverse=True)

    return render(request, "sms_history.html", {"sms_data": sms_data, "message": message})
