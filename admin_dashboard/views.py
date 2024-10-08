from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from core.semaphore import fetch_sms_data
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.db import transaction

from core.decorators import staff_required

from record_management.models import Client, Pet
from record_management.forms import UserUpdateForm, ClientUpdateForm, TwoFactorAuthenticationForm, AdminTwoFactorAuthenticationForm
from billing_management.models import Billing
from appointment_management.models import Appointment
from core.models import SMSLogs

import urllib.parse
import requests
import json

from django.contrib.auth.models import User, Group
from core.models import Province, Municipality, Barangay

from django.contrib.sessions.models import Session

@login_required
@staff_required
def update_user(request, userID):
    user = get_object_or_404(User, pk=userID)
    client = get_object_or_404(Client, user=user)
    
    if not user.is_staff:
        return redirect('user-list-page')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        client_form = ClientUpdateForm(request.POST, instance=client)
        
        if 'province' in request.POST:
            client_form.fields['city'].queryset = Municipality.objects.filter(province_id=request.POST['province'])
        if 'city' in request.POST:
            client_form.fields['barangay'].queryset = Barangay.objects.filter(municipality_id=request.POST['city'])

        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            client_form.save()
            return redirect('update-user-page', userID=userID)
    else:
        user_form = UserUpdateForm(instance=user)
        client_form = ClientUpdateForm(instance=client)

    province = Province.objects.filter(name=client.province).first()
    municipality = Municipality.objects.filter(name=client.city, province=province).first()
    barangay = Barangay.objects.filter(name=client.barangay, municipality=municipality).first()

    address_dict = {
        'province': province.id if province else None,
        'municipality': municipality.id if municipality else None,
        'barangay': barangay.id if barangay else None,
    }

    context = {
        'user_form': user_form,
        'client_form': client_form,
        'user_id': userID,
        'user': user,
        'client': client,
        'address': address_dict,
    }

    return render(request, 'update_user.html', context)

@login_required
@staff_required
def update_2fa(request, userID):
    user = get_object_or_404(User, pk=userID)
    client = get_object_or_404(Client, user=user)

    if not user.is_staff:
        return redirect('user-list-page')

    if request.method == 'POST':
        two_factor_form = AdminTwoFactorAuthenticationForm(request.POST)
        
        if two_factor_form.is_valid():
            client.two_auth_enabled = two_factor_form.cleaned_data['two_auth_enabled']
            client.contact_number = two_factor_form.cleaned_data['phone_number']
            client.save()
            messages.success(request, 'Two-factor authentication settings successfully updated!')
            return redirect('update-user-2fa-page', userID=userID)
        else:
            for error in two_factor_form.non_field_errors():
                messages.error(request, error)
            for field, errors in two_factor_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        two_factor_form = AdminTwoFactorAuthenticationForm(initial={'two_auth_enabled': user.client.two_auth_enabled, 'phone_number': user.client.contact_number})

    return render(request, 'update_2fa.html', {'two_factor_form': two_factor_form, 'sms_number': user.client.contact_number, 'user_id': userID, 'user': user})

@login_required
@staff_required
def ban_user(request, userID):
    try:
        with transaction.atomic():
            user = get_object_or_404(User, pk=userID)
            client = get_object_or_404(Client, user=user)

            if user.is_staff:
                return JsonResponse({'success': False, 'message': 'Cannot ban staff.'})

            user.is_active = False
            client.isBanned = True
            client.ban_reason = request.POST['reason']
            user.save()
            client.save()

            all_sessions  = Session.objects.filter(expire_date__gte=datetime.now())
            for session in all_sessions:
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id'):
                    if int(session_data.get('_auth_user_id')) == int(user.id):
                        session.delete()

            return JsonResponse({'success': True, 'message': 'User banned.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Something went wrong.'})

@login_required
@staff_required
def unban_user(request, userID):
    try:
        with transaction.atomic():
            user = get_object_or_404(User, pk=userID)
            client = get_object_or_404(Client, user=user)
            user.is_active = True
            client.isBanned = False
            user.save()
            client.save()
            return JsonResponse({'success': True, 'message': 'User unbanned.'})
    except:
        return JsonResponse({'success': False, 'message': 'Something went wrong.'})

@login_required
@staff_required
def promote_user(request, userID):
    try:
        with transaction.atomic():
            secretary_group = Group.objects.get(name='Secretary')
            if not secretary_group:
                return JsonResponse({'success': False, 'message': 'Secretary group not found.'})

            user = get_object_or_404(User, pk=userID)
            user.is_staff = True
            user.save()
            secretary_group.user_set.add(user)

    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Something went wrong: {}'.format(e)})
    return JsonResponse({'success': True, 'message': 'User promoted successfully.'})

@login_required
@staff_required
def demote_user(request, userID):
    try:
        with transaction.atomic():
            secretary_group = Group.objects.get(name='Secretary')
            if not secretary_group:
                return JsonResponse({'success': False, 'message': 'Secretary group not found.'})

            user = get_object_or_404(User, pk=userID)
            user.is_staff = False
            user.save()
            secretary_group.user_set.remove(user)

    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Something went wrong: {}'.format(e)})
    return JsonResponse({'success': True, 'message': 'User demoted successfully.'})

@login_required
@staff_required
def admin_dashboard(request):
    clients = Client.objects.filter(user__is_active=True)
    client_count = clients.count()
    pets = Pet.objects.all()
    pet_count = pets.count()

    # Get total gross revenue for today
    today = datetime.now()
    today_bills = Billing.objects.filter(date_created__year=today.year, date_created__month=today.month, date_created__day=today.day, isActive=True, isPaid=True)
    total_revenue = 0
    for bill in today_bills:
        total_revenue += bill.get_total()

    in_30_days = today + timedelta(days=30)
    upcoming_appointments = Appointment.objects.filter(date__range=[today, in_30_days], isActive=True, status='pending').order_by('date')

    today_appointments = Appointment.objects.filter(date__year=today.year, date__month=today.month, date__day=today.day, isActive=True)
    appointment_count = today_appointments.count()

    today_done_appointments = Appointment.objects.filter(date__year=today.year, date__month=today.month, date__day=today.day, isActive=True, status='done')
    done_appointment_count = today_appointments.count()

    monthly_revenue = [0]*12

    current_year_bills = Billing.objects.filter(date_created__year=today.year, isActive=True, isPaid=True)

    for month in range(1, 13): 
        month_bills = current_year_bills.filter(date_created__month=month, isActive=True, isPaid=True)
        for bill in month_bills:
            monthly_revenue[month-1] += bill.get_total() 

    current_year = datetime.now().year
    start_year = current_year - 6
    yearly_revenue = {}

    for year in range(start_year, current_year + 1): 
        year_bills = Billing.objects.filter(date_created__year=year, isActive=True, isPaid=True)
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
    # raw_sms_data = fetch_sms_data()

    # if isinstance(raw_sms_data, str):
    #     message = raw_sms_data
    #     sms_data = None
    # else:
    #     message = None
    #     sms_data = []
    #     for sms in raw_sms_data:
    #         formatted_date_sent = datetime.strptime(sms['created_at'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y - %I:%M %p")
    #         sms['created_at'] = formatted_date_sent
    #         sms_data.append(sms)

    #     sms_data.sort(key=lambda x: x['created_at'], reverse=True)

    sms_logs = SMSLogs.objects.all().order_by('-id')
    #return render(request, "sms_history.html", {"sms_data": sms_data, "message": message, "sms_logs": sms_logs})

    modified_sms_logs = [
        {
            'id': sms_log.id,
            'text': sms_log.text,
            'client': sms_log.client,
            'date_created': sms_log.date_created,
            'sms_type': 'Day' if sms_log.sms_type == 'daily' else sms_log.sms_type.replace('ly', ''),
        }
        for sms_log in sms_logs
    ]

    return render(request, "sms_history.html", {"sms_logs": modified_sms_logs})
