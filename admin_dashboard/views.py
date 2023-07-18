from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from core.semaphore import fetch_sms_data
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.core.serializers.json import DjangoJSONEncoder

from core.decorators import staff_required

from record_management.models import Client, Pet
from billing_management.models import Billing
from appointment_management.models import Appointment
from core.models import SMSLogs

import urllib.parse
import requests
import json

from django.contrib.auth.models import User

@login_required
@staff_required
def admin_dashboard(request):
    # Get count of clients
    clients = Client.objects.filter(user__is_staff=False, user__is_superuser=False)
    client_count = clients.count()
    # Get count of pets
    pets = Pet.objects.filter(client__user__is_staff=False, client__user__is_superuser=False)
    pet_count = pets.count()

    # Get total gross revenue for today
    today = datetime.now()
    today_bills = Billing.objects.filter(date_created__year=today.year, date_created__month=today.month, date_created__day=today.day, isActive=True)
    total_revenue = 0
    for bill in today_bills:
        total_revenue += bill.get_total()

    in_30_days = today + timedelta(days=30)
    upcoming_appointments = Appointment.objects.filter(date__range=[today, in_30_days], isActive=True, status='pending')

    today_appointments = Appointment.objects.filter(date__year=today.year, date__month=today.month, date__day=today.day, isActive=True)
    appointment_count = today_appointments.count()

    today_done_appointments = Appointment.objects.filter(date__year=today.year, date__month=today.month, date__day=today.day, isActive=True, status='done')
    done_appointment_count = today_appointments.count()

    monthly_revenue = [0]*12

    current_year_bills = Billing.objects.filter(date_created__year=today.year, isActive=True)

    for month in range(1, 13): 
        month_bills = current_year_bills.filter(date_created__month=month)
        for bill in month_bills:
            monthly_revenue[month-1] += bill.get_total() 

    current_year = datetime.now().year
    start_year = current_year - 6
    yearly_revenue = {}

    for year in range(start_year, current_year + 1): 
        year_bills = Billing.objects.filter(date_created__year=year, isActive=True)
        yearly_revenue[str(year)] = sum(bill.get_total() for bill in year_bills)

    context = {
        'client_count': client_count, 
        'pet_count': pet_count, 
        'total_revenue': total_revenue,
        'upcoming_appointments': upcoming_appointments,
        'appointment_count': appointment_count,
        'done_appointment_count': done_appointment_count,
        'monthly_revenue': json.dumps(monthly_revenue, cls=DjangoJSONEncoder),
        'yearly_revenue': json.dumps(yearly_revenue, cls=DjangoJSONEncoder),
    }
    
    return render(request, 'admin_dashboard.html', context)


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

    sms_logs = SMSLogs.objects.all().order_by('-id')

    return render(request, "sms_history.html", {"sms_data": sms_data, "message": message, "sms_logs": sms_logs})
