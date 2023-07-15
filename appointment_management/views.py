from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from record_management.models import Client, Pet
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page
from django.conf import settings
from datetime import datetime, date
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from core.semaphore import send_sms, send_otp_sms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q
from django.forms.models import model_to_dict
from django.core import serializers

from core.decorators import staff_required
from .models import Appointment, DoctorSchedule

from .forms import AppointmentForm, RebookAppointmentForm, DisableDayForm, AppointmentFormClient, RebookAppointmentFormClient

import json
import requests
import time

MAX_APPOINTMENTS_PER_DAY = 8


#--------------------ADMIN SIDE------------------------------------
@login_required 
@staff_required
def disable_day(request):
    if request.method == 'POST':
        form = DisableDayForm(request.POST)

        if form.is_valid():
            disable_day = form.save(commit=False)
            disable_day.date = request.POST.get('date')
            disable_day.isActive = True
            disable_day.save()

            if disable_day.timeOfTheDay == 'whole_day':
                Appointment.objects.filter(date=disable_day.date).update(status='rebook')
            else:
                Appointment.objects.filter(date=disable_day.date, timeOfTheDay=disable_day.timeOfTheDay).update(status='rebook')

            disable_day.send_message_to_client()

            return JsonResponse({'status': 'success'}, status=200)

        else:
            return JsonResponse({'status': 'error', 'message': str(form.errors)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def get_disabled_days(request):
    disabled_days = DoctorSchedule.objects.filter(isActive=True).values('date', 'timeOfTheDay')
    disabled_days_list = list(disabled_days)

    return JsonResponse(disabled_days_list, safe=False)

@login_required
@staff_required
def is_day_disabled(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        disabled_day = DoctorSchedule.objects.filter(date=selected_date, isActive=True).first()

        if disabled_day:
            return JsonResponse({
                'is_disabled': True,
                'time_of_the_day': disabled_day.timeOfTheDay
            }, status=200)
        else:
            return JsonResponse({
                'is_disabled': False,
                'time_of_the_day': None
            }, status=200)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required 
@staff_required
def enable_day(request):
    date = request.POST.get('date')
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    DoctorSchedule.objects.filter(date=date_obj).delete()
    return JsonResponse({'success': True})

@login_required
@staff_required
def calendar(request):
    clients_list = Client.objects.all().order_by('id')
    rebook_appointments = Appointment.objects.filter(status='rebook')

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

    form = AppointmentForm()
    rebook_form = RebookAppointmentForm()
    disable_day_form = DisableDayForm()

    context = {
        'clients': clients_list,
        'total_clients': clients_list.count(),
        'form': form,
        'rebook_appointments': rebook_appointments,
        'rebook_form': rebook_form,
        'disable_day_form': disable_day_form,
    }

    return render(request, 'admin/calendar.html', context)

@csrf_exempt
@login_required
@staff_required
def send_sms_to_client(request):
    if request.method == 'POST':
        contact_numbers = json.loads(request.POST.get('phone_numbers'))
        appointment_ids = json.loads(request.POST.get('appointment_id'))

        if appointment_ids:
            if type(appointment_ids) == list:
                for appointment_id in appointment_ids:
                    try:
                        appointment = Appointment.objects.get(pk=appointment_id)
                        appointment.remindClient()
                    except Appointment.DoesNotExist:
                        return JsonResponse({"status": "error", "message": f"No appointment found with ID {appointment_id}"})
            elif type(appointment_ids) == int:
                try:
                    appointment = Appointment.objects.get(pk=appointment_ids)
                    appointment.remindClient()
                except Appointment.DoesNotExist:
                    return JsonResponse({"status": "error", "message": f"No appointment found with ID {appointment_ids}"})

            return JsonResponse({"status": "success", "message": "SMS sent successfully"})
        else:
            return JsonResponse({"status": "error", "message": "No clients found or No appointments found"})

@csrf_exempt
@login_required
@staff_required
def set_appointment(request):
    if request.method == 'POST':
        try:
            client_id = request.POST['client']
            pet_id = request.POST['pet']
            time_of_day = request.POST['timeOfTheDay']

            iso_timestamp = request.POST['date']
            print(iso_timestamp)
            datetime_object = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
            
            datetime_object = datetime_object.replace(tzinfo=timezone.utc).astimezone(timezone.get_current_timezone())

            date = datetime_object.date().isoformat()

            service_id = request.POST['purpose']
            status = 'pending'
            
            appointment = Appointment(client_id=client_id, pet_id=pet_id, timeOfTheDay=time_of_day, 
                                      date=date, purpose_id=service_id, status=status, isActive=True)
            appointment.save()
            
            return JsonResponse({'message': 'Appointment created successfully'})
        except MultiValueDictKeyError:
            return JsonResponse({'error': 'One of the required keys is missing from the form data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@staff_required
def get_appointments(request):
    appointments = Appointment.objects.filter(status='pending', isActive=True, pet__is_active=True).order_by('-timeOfTheDay')

    event_list = []
    for appointment in appointments:
        event = {
            'id': appointment.id,
            'title': f'#{appointment.id} - {appointment.client.full_name}',
            'start': appointment.date.isoformat(),
            'color': appointment.getTimeOfDayColor(),
            'extendedProps': {
                'client_id': appointment.client.id,
                'client': appointment.client.full_name,
                'contact_number': appointment.client.contact_number,
                'pet': appointment.pet.name,  
                'pet_id': appointment.pet.id,
                'timeOfTheDay': appointment.get_timeOfTheDay_display(),
                'timeOfTheDay_val': appointment.timeOfTheDay,
                'purpose': appointment.purpose.service_type,
                'purpose_id': appointment.purpose.id,
                'current_date': appointment.date.isoformat(),
            }
        }
        event_list.append(event)

    return JsonResponse(event_list, safe=False)

@login_required
@csrf_exempt
def cancel_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.isActive = False
            appointment.status = 'cancelled'
            appointment.save()
            return JsonResponse({"status": "Appointment cancelled successfully"})
        except Appointment.DoesNotExist:
            return JsonResponse({"status": "Appointment does not exist"})
    else:
        return JsonResponse({"status": "Invalid request method"})

@login_required
@csrf_exempt
def add_to_rebook_list(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.status = "rebook"
            #appointment.isActive = False
            appointment.save()
            return JsonResponse({'status': 'Appointment rebooked successfully'}, status=200)
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'Appointment not found'}, status=404)
    else:
        return JsonResponse({'status': 'Invalid method'}, status=400)

@login_required
@csrf_exempt
def rebook_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_date_str = request.POST.get('new_date')
        pet_id = request.POST.get('pet')
        purpose_id = request.POST.get('purpose')
        time_of_the_day = request.POST.get('time_of_day')

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            appointment.date = new_date_str
            appointment.pet_id = pet_id
            appointment.purpose_id = purpose_id
            appointment.timeOfTheDay = time_of_the_day
            appointment.status = "pending"
            
            appointment.save()
            
            return JsonResponse({'status': 'Appointment rebooked successfully'}, status=200)

        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'Appointment not found'}, status=404)
        except ValueError:
            return JsonResponse({'status': 'Invalid data'}, status=400)
    else:
        return JsonResponse({'status': 'Invalid method'}, status=400)

@login_required
@csrf_exempt
def check_if_full(request):
    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date')
        try:
            selected_date = datetime.strptime(selected_date_str.split('T')[0], "%Y-%m-%d").date()  # convert string to date
            num_appointments = Appointment.objects.filter(date=selected_date, status='pending').count()
            if num_appointments >= 8:
                return JsonResponse({'status': 'full'}, status=200)
            else:
                return JsonResponse({'status': 'not full'}, status=200)
        except ValueError:
            return JsonResponse({'status': 'Invalid date format'}, status=400)
    else:
        return JsonResponse({'status': 'Invalid method'}, status=400)

@login_required
@staff_required
def get_pets(request):
    client_id = request.GET.get('client_id')
    pets = Pet.objects.filter(client=client_id).values('id', 'name')
    return JsonResponse(list(pets), safe=False)

# @login_required
# @staff_required
# def get_pets(request):
#     client_id = request.GET.get('client_id')
#     pets = Pet.objects.filter(client=client_id).exclude(appointment__isnull=False).values('id', 'name')
#     return JsonResponse(list(pets), safe=False)

@login_required
@staff_required
@csrf_exempt
def set_appointment_done(request):
    if request.method == 'POST':
        try:
            appointment_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.status = 'done'
            appointment.isActive = False
            appointment.save()
            return JsonResponse({'status': 'Appointment marked as done successfully'})
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


#--------------------CLIENT SIDE------------------------------------
@login_required
def client_calendar(request):
    client = Client.objects.get(user=request.user)
    pet_id = request.GET.get('pet_id')
    if pet_id:
        form = AppointmentFormClient(request.POST or None, initial={'pet': pet_id}, request=request)
        #form.fields['pet'].widget.attrs['disabled'] = True
    else:
        form = AppointmentFormClient(request.POST or None, request=request)
    rebook_appointments = Appointment.objects.filter(status='rebook', client=client)

    rebook_form = RebookAppointmentFormClient(request.POST or None, request=request)

    context = {
        'form': form,
        'client': client,
        'rebook_appointments': rebook_appointments,
        'rebook_form': rebook_form
    }

    return render(request, 'client/calendar.html', context)

@login_required
@csrf_exempt
def set_appointment_client(request):
    if request.method == 'POST':
        try:
            pet_id = request.POST['pet']
            time_of_day = request.POST['timeOfTheDay']
            iso_timestamp = request.POST['date']
            
            datetime_object = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
            
            datetime_object = datetime_object.replace(tzinfo=timezone.utc).astimezone(timezone.get_current_timezone())

            date = datetime_object.date().isoformat()

            service_id = request.POST['purpose']
            status = 'pending'
            
            appointment = Appointment(client_id=request.user.client.id, pet_id=pet_id, timeOfTheDay=time_of_day, 
                                      date=date, purpose_id=service_id, status=status, isActive=True)
            appointment.save()
            
            return JsonResponse({'message': 'Appointment created successfully'})
        except MultiValueDictKeyError:
            return JsonResponse({'error': 'One of the required keys is missing from the form data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_appointments_client(request):
    appointments = Appointment.objects.filter(client=request.user.client, status='pending', isActive=True, pet__is_active=True).order_by('-timeOfTheDay')

    event_list = []
    for appointment in appointments:
        event = {
            'id': appointment.id,
            'title': f'#{appointment.id} - {appointment.pet.name}',
            'start': appointment.date.isoformat(),
            'color': appointment.getTimeOfDayColor(),
            'extendedProps': {
                'client_id': appointment.client.id,
                'client': appointment.client.full_name,
                'contact_number': appointment.client.contact_number,
                'pet': appointment.pet.name,  
                'pet_id': appointment.pet.id,
                'timeOfTheDay': appointment.get_timeOfTheDay_display(),
                'timeOfTheDay_val': appointment.timeOfTheDay,
                'purpose': appointment.purpose.service_type,
                'purpose_id': appointment.purpose.id,
                'current_date': appointment.date.isoformat(),
            }
        }
        event_list.append(event)

    return JsonResponse(event_list, safe=False)

@login_required
def is_all_my_pets_scheduled(request):
    client_pets = Pet.objects.filter(client=request.user.client)
    pets_with_appointments = Appointment.objects.exclude(status='cancelled').filter(pet__in=client_pets, status__in=['pending', 'rebook']).values_list('pet', flat=True).distinct()

    if client_pets.count() == pets_with_appointments.count():
        return JsonResponse({'all_scheduled': True})
    else:
        return JsonResponse({'all_scheduled': False})

@login_required
def get_appointments_count(request):
    appointments = Appointment.objects.filter(status__in=['pending', 'rebook'])
    appointment_counts = {}
    for appointment in appointments:
        date_str = appointment.date.strftime('%Y-%m-%d')
        if date_str in appointment_counts:
            appointment_counts[date_str] += 1
        else:
            appointment_counts[date_str] = 1

    return JsonResponse(appointment_counts)

@login_required
def get_pets_client(request):
    client_id = request.GET.get('client_id')
    selected_pet_id = request.GET.get('selected_pet_id')

    pets_with_appointments = Appointment.objects.exclude(
        status__in=['cancelled', 'done']).filter(pet__client=client_id).values_list('pet', flat=True)
    
    pets_without_appointments = Pet.objects.filter(client=client_id, is_active=True).exclude(id__in=pets_with_appointments).values('id', 'name')
    selected_pet = Pet.objects.filter(id=selected_pet_id, is_active=True).values('id', 'name')

    pets = pets_without_appointments | selected_pet
    
    return JsonResponse(list(pets), safe=False)
