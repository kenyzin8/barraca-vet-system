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
from django.db.models import Count

from core.decorators import staff_required
from .models import Appointment, DoctorSchedule, MaximumAppointment, DateSlot

from .forms import *

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
            date = request.POST.get('date')

            existing_disabled_day = DoctorSchedule.objects.filter(date=date, isActive=True).first()
            if existing_disabled_day:
                return JsonResponse({'status': 'error', 'message': 'This date is already disabled, please refresh the page.'}, status=400)

            disable_day = form.save(commit=False)
            disable_day.date = date
            disable_day.isActive = True
            disable_day.save()

            disable_day.send_message_to_client()

            if disable_day.timeOfTheDay == 'whole_day':
                Appointment.objects.filter(date=disable_day.date, isActive=True, status='pending').update(status='rebook')
            else:
                Appointment.objects.filter(date=disable_day.date, timeOfTheDay=disable_day.timeOfTheDay, isActive=True, status='pending').update(status='rebook')

            disabled_day_dict = model_to_dict(disable_day, exclude=['id', 'isActive', 'reason'])

            disabled_day_dict['date'] = disable_day.date
            disabled_day_dict['timeOfTheDay'] = disable_day.timeOfTheDay
            disabled_day_dict['reason'] = disable_day.reason

            return JsonResponse({'status': 'success', 'disabled_day': disabled_day_dict}, status=200)

        else:
            return JsonResponse({'status': 'error', 'message': str(form.errors)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

# @login_required
# def get_max_appointments(request):
#     max_appointments = MaximumAppointment.load()
#     return JsonResponse({'max_appointments': max_appointments.max_appointments}, status=200)

# @login_required
# def get_date_slots(request):
#     date_slots = DateSlot.objects.filter(isActive=True).values('date', 'slots')
#     date_slots_list = list(date_slots)

#     return JsonResponse(date_slots_list, safe=False)

@csrf_exempt
def adjust_slots(request):
    if request.method == "POST":
        form = DateSlotForm(request.POST)
        
        if form.is_valid():
            date = request.POST.get('date')
            morning_slots = form.cleaned_data.get('morning_slots')
            afternoon_slots = form.cleaned_data.get('afternoon_slots')

            if morning_slots < 1:
                return JsonResponse({'status': 'error', 'message': 'Please enter a number greater than or equal to 1 for morning.'})
            elif morning_slots > MAX_APPOINTMENTS_PER_DAY:
                return JsonResponse({'status': 'error', 'message': f'Please enter a number less than or equal to {MAX_APPOINTMENTS_PER_DAY}.'})
            elif afternoon_slots < 1:
                return JsonResponse({'status': 'error', 'message': 'Please enter a number greater than or equal to 1 for afternoon.'})
            elif afternoon_slots > MAX_APPOINTMENTS_PER_DAY:
                return JsonResponse({'status': 'error', 'message': f'Please enter a number less than or equal to {MAX_APPOINTMENTS_PER_DAY}.'})

            appointment_count_morning = Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='morning').count()
            appointment_count_afternoon = Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='afternoon').count()

            if morning_slots < appointment_count_morning:
                return JsonResponse({'status': 'error', 'message': f'There are already {appointment_count_morning} morning appointments on this date. Please choose a number value greater than or equal to this.'})
            elif afternoon_slots < appointment_count_afternoon:
                return JsonResponse({'status': 'error', 'message': f'There are already {appointment_count_afternoon} afternoon appointments on this date. Please choose a number value greater than or equal to this.'})

            dateSlot, created = DateSlot.objects.get_or_create(date=date, defaults={'morning_slots': morning_slots, 'afternoon_slots': afternoon_slots})
    
            if not created:
                dateSlot.morning_slots = morning_slots
                dateSlot.afternoon_slots = afternoon_slots
                dateSlot.save()

            return JsonResponse({
                'status': 'success', 
                'message': 'Slots adjusted successfully',
                'dateSlot': {
                    'date': date,
                    'morning_slots': morning_slots,
                    'afternoon_slots': afternoon_slots,
                }
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'Failed to adjust slots', 'errors': errors})

# @login_required
# def get_disabled_days(request):
#     disabled_days = DoctorSchedule.objects.filter(isActive=True).values('date', 'timeOfTheDay')
#     disabled_days_list = list(disabled_days)

#     return JsonResponse(disabled_days_list, safe=False)

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
    if request.method == 'POST':
        date = request.POST.get('date')
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        existing_doctor_schedule = DoctorSchedule.objects.filter(date=date_obj).first()
        
        if not existing_doctor_schedule:
            return JsonResponse({'status': 'error', 'message': 'This date is already enabled, please refresh the page.'}, status=400)

        DoctorSchedule.objects.filter(date=date_obj).delete()
        return JsonResponse({'success': True, 'message': f'{date} has been enabled.'}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

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
    slots_form = DateSlotForm()
    change_time_form = ChangeTimeForm()

    context = {
        'clients': clients_list,
        'total_clients': clients_list.count(),
        'form': form,
        'rebook_appointments': rebook_appointments,
        'rebook_form': rebook_form,
        'disable_day_form': disable_day_form,
        'slots_form': slots_form,
        'change_time_form': change_time_form,
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
                        appointment.remindClient('renotify')
                    except Appointment.DoesNotExist:
                        return JsonResponse({"status": "error", "message": f"No appointment found with ID {appointment_id}"})
            elif type(appointment_ids) == int:
                try:
                    appointment = Appointment.objects.get(pk=appointment_ids)
                    appointment.remindClient('renotify')
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
            
            time = request.POST['time']

            if time >= '12:00:00' and time < '18:00:00':
                time_of_day = 'afternoon'
            else:
                time_of_day = 'morning'

            iso_timestamp = request.POST['date']

            datetime_object = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
            
            datetime_object = datetime_object.replace(tzinfo=timezone.utc).astimezone(timezone.get_current_timezone())

            date = datetime_object.date().isoformat()

            disabled_day = DoctorSchedule.objects.filter(date=date).first()
            if disabled_day and disabled_day.isActive and (disabled_day.timeOfTheDay == time_of_day or disabled_day.timeOfTheDay == 'whole_day'):
                return JsonResponse({'status': 'error', 'message': 'The chosen date and time is disabled for appointments'}, status=400)

            service_id = request.POST['purpose']

            service = Service.objects.get(pk=service_id)

            existing_appointment = Appointment.objects.filter(date=date, time=time, isActive=True).first()

            if existing_appointment:
                existing_service = existing_appointment.purpose
                if existing_service.job_for == 'doctor' and service.job_for == 'doctor':
                    return JsonResponse({'status': 'error', 'message': 'A doctor is already booked for a service at this time.'}, status=400)

            status = 'pending'
            
            date_slot = DateSlot.objects.filter(date=date).first()
            maximum_appointments = MaximumAppointment.load()

            doctor_schedule = DoctorSchedule.objects.filter(date=date, isActive=True).first()
            
            if date_slot:
                if time_of_day == 'morning':
                    morning_slots_remaining = date_slot.morning_slots - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='morning').count()
                    
                    if morning_slots_remaining != 1:
                        morning_slots_remaining -= 1

                    if morning_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for morning on this date.'}, status=400)
                elif time_of_day == 'afternoon':
                    afternoon_slots_remaining = date_slot.afternoon_slots - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                    if afternoon_slots_remaining != 1:
                        afternoon_slots_remaining -= 1
                    
                    if afternoon_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for afternoon on this date.'}, status=400)
            elif not date_slot:
                if time_of_day == 'morning':
                    morning_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='morning').count()
                    
                    if morning_slots_remaining != 1:
                        morning_slots_remaining -= 1

                    if morning_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for morning on this date.'}, status=400)
                elif time_of_day == 'afternoon':
                    afternoon_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                    if afternoon_slots_remaining != 1:
                        afternoon_slots_remaining -= 1

                    if afternoon_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for afternoon on this date.'}, status=400)
            else:
                if doctor_schedule:
                    if doctor_schedule.timeOfTheDay == 'afternoon' and time_of_day == 'morning':
                        
                        morning_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='morning').count()

                        if morning_slots_remaining != 1:
                            morning_slots_remaining -= 1
                        
                        if morning_slots_remaining <= 0:
                            return JsonResponse({'status': 'error', 'message': 'No more slots available for morning on this date.'}, status=400)

                    elif doctor_schedule.timeOfTheDay == 'morning' and time_of_day == 'afternoon':
                        
                        afternoon_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                        
                        if afternoon_slots_remaining != 1:
                            afternoon_slots_remaining -= 1
                        
                        if afternoon_slots_remaining <= 0:
                            return JsonResponse({'status': 'error', 'message': 'No more slots available for afternoon on this date.'}, status=400)

            if Appointment.objects.filter(date=date, isActive=True, status='pending').count() >= maximum_appointments.max_appointments:
                    return JsonResponse({'status': 'error', 'message': 'No more slots available for this date.'}, status=400)

            appointment = Appointment(client_id=client_id, pet_id=pet_id, timeOfTheDay=time_of_day, 
                                      date=date, time=time, purpose_id=service_id, status=status, isActive=True)
            appointment.save()
            
            appointment_dict = model_to_dict(appointment)

            appointment_dict['pet'] = model_to_dict(appointment.pet, exclude=['picture'])
            appointment_dict['client'] = model_to_dict(appointment.client)
            appointment_dict['color'] = appointment.getTimeOfDayColor()
            appointment_dict['timeOfTheDay'] = appointment.get_timeOfTheDay_display()
            appointment_dict['timeOfTheDay_val'] = appointment.timeOfTheDay
            appointment_dict['time'] = appointment.time
            appointment_dict['purpose'] = appointment.purpose.service_type
            appointment_dict['purpose_id'] = appointment.purpose.id
 
            return JsonResponse({'success': True, 'message': 'Appointment created successfully', 'appointment': appointment_dict})
        except MultiValueDictKeyError:
            return JsonResponse({'error': 'One of the required keys is missing from the form data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@staff_required
def get_busy_times_for_service(request):
    date_str = request.GET.get('date', None)
    service_id = request.GET.get('service_id', None)

    if not date_str or not service_id:
        return JsonResponse({'status': 'error', 'message': 'Date or service_id parameter is missing.'}, status=400)

    try:
        job_required = Service.objects.get(pk=service_id).job_for
    except Service.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid service ID.'}, status=400)

    busy_appointments = Appointment.objects.filter(date=date_str, status='pending', isActive=True, purpose__job_for=job_required)

    busy_times = [appointment.time.strftime('%H:%M:%S') for appointment in busy_appointments]

    return JsonResponse({'status': 'success', 'busy_times': busy_times})

# @login_required
# @staff_required
# def get_appointments(request):
#     appointments = Appointment.objects.filter(status='pending', isActive=True, pet__is_active=True).order_by('-timeOfTheDay')
#     event_list = []
#     for appointment in appointments:
#         event = {
#             'id': appointment.id,
#             #'title': f'#{appointment.id} - {appointment.client.full_name}',
#             'title': f'{appointment.client.full_name}',
#             'start': appointment.date.isoformat(),
#             'color': appointment.getTimeOfDayColor(),
#             'extendedProps': {
#                 'client_id': appointment.client.id,
#                 'client': appointment.client.full_name,
#                 'contact_number': appointment.client.contact_number,
#                 'pet': appointment.pet.name,  
#                 'pet_id': appointment.pet.id,
#                 'timeOfTheDay': appointment.get_timeOfTheDay_display(),
#                 'timeOfTheDay_val': appointment.timeOfTheDay,
#                 'purpose': appointment.purpose.service_type,
#                 'purpose_id': appointment.purpose.id,
#                 'current_date': appointment.date.isoformat(),
#                 'day_sms_reminder': appointment.daily_reminder_sent,
#                 'week_sms_reminder': appointment.weekly_reminder_sent,
#             }
#         }
#         event_list.append(event)
        
#     return JsonResponse(event_list, safe=False)

@login_required
@csrf_exempt
def cancel_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        reason = request.POST.get('reason')

        if not reason:
            return JsonResponse({"status": "error", "message": "Please enter a reason for cancelling the appointment."}, status=400)

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if appointment.status == 'cancelled':
                return JsonResponse({"status": "error", "message": "This appointment is already cancelled, please refresh the page."}, status=400)
            appointment.isActive = False
            appointment.status = 'cancelled'
            appointment.remindClientCancel(reason)
            appointment.save()

            return JsonResponse({"status": "Appointment cancelled successfully", "pet": model_to_dict(appointment.pet, exclude=['picture']),"appointment_date": appointment.date.strftime("%Y-%m-%d")})
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
            if appointment.status == 'rebook':
                return JsonResponse({"status": "error", "message": "This appointment is already marked for rebooking, please refresh the page."}, status=400)
            appointment.status = "rebook"
            #appointment.date = None
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
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()

        pet_id = request.POST.get('pet')
        
        purpose_id = request.POST.get('purpose')
        
        time = request.POST.get('time')
        
        if time >= '12:00:00' and time < '18:00:00':
            time_of_the_day = 'afternoon'
        elif time > '00:00:00' and time < '12:00:00':
            time_of_the_day = 'morning'
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid time.'}, status=400)

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if appointment.pet.id != int(pet_id):
               return JsonResponse({'status': 'error', 'message': 'You cannot change your pet during rebooking.'}, status=400)

            disabled_day = DoctorSchedule.objects.filter(date=new_date, isActive=True).first() 

            if disabled_day:
                if disabled_day.timeOfTheDay == 'whole_day' or disabled_day.timeOfTheDay == time_of_the_day:
                    return JsonResponse({'status': 'error', 'message': 'The chosen date is disabled, please refresh the page.'}, status=400)

            date_slot = DateSlot.objects.filter(date=new_date).first()
            maximum_appointments = MaximumAppointment.load()
            doctor_schedule = DoctorSchedule.objects.filter(date=new_date, isActive=True).first()

            if date_slot:
                if time_of_the_day == 'morning':
                    morning_slots_remaining = date_slot.morning_slots - Appointment.objects.filter(date=new_date, isActive=True, status='pending', timeOfTheDay='morning').count()
                    if morning_slots_remaining != 1:
                        morning_slots_remaining -= 1

                    if morning_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more morning slots available for this date.'}, status=400)
                elif time_of_the_day == 'afternoon':
                    afternoon_slots_remaining = date_slot.afternoon_slots - Appointment.objects.filter(date=new_date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                    if afternoon_slots_remaining != 1:
                        afternoon_slots_remaining -= 1

                    if afternoon_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more afternoon slots available for this date.'}, status=400)
            elif not date_slot:
                if time_of_the_day == 'morning':
                    morning_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=new_date, isActive=True, status='pending', timeOfTheDay='morning').count()
                    
                    if morning_slots_remaining != 1:
                        morning_slots_remaining -= 1

                    if morning_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for morning on this date.'}, status=400)
                elif time_of_the_day == 'afternoon':
                    afternoon_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=new_date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                    if afternoon_slots_remaining != 1:
                        afternoon_slots_remaining -= 1

                    if afternoon_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for afternoon on this date.'}, status=400)
            else:
                if doctor_schedule:
                    if doctor_schedule.timeOfTheDay == 'afternoon' and time_of_the_day == 'morning':
                        
                        morning_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=new_date, isActive=True, status='pending', timeOfTheDay='morning').count()

                        if morning_slots_remaining != 1:
                            morning_slots_remaining -= 1
                        
                        if morning_slots_remaining <= 0:
                            return JsonResponse({'status': 'error', 'message': 'No more slots available for morning on this date.'}, status=400)

                    elif doctor_schedule.timeOfTheDay == 'morning' and time_of_the_day == 'afternoon':
                        
                        afternoon_slots_remaining = (maximum_appointments.max_appointments // 2) - Appointment.objects.filter(date=new_date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                        
                        if afternoon_slots_remaining != 1:
                            afternoon_slots_remaining -= 1
                        
                        if afternoon_slots_remaining <= 0:
                            return JsonResponse({'status': 'error', 'message': 'No more slots available for afternoon on this date.'}, status=400)

            if Appointment.objects.filter(date=new_date, isActive=True, status='pending').count() >= maximum_appointments.max_appointments:
                    return JsonResponse({'status': 'error', 'message': 'No more slots available for this date.'}, status=400)

            appointment.date = new_date
            appointment.pet_id = pet_id
            appointment.purpose_id = purpose_id
            appointment.timeOfTheDay = time_of_the_day
            appointment.time = time
            appointment.status = "pending"
            
            appointment.save()
        
            appointment_dict = model_to_dict(appointment)

            appointment_dict['pet'] = model_to_dict(appointment.pet, exclude=['picture'])
            appointment_dict['client'] = model_to_dict(appointment.client)
            appointment_dict['color'] = appointment.getTimeOfDayColor()
            appointment_dict['timeOfTheDay'] = appointment.get_timeOfTheDay_display()
            appointment_dict['timeOfTheDay_val'] = appointment.timeOfTheDay
            appointment_dict['time'] = appointment.time
            appointment_dict['purpose'] = appointment.purpose.service_type
            appointment_dict['purpose_id'] = appointment.purpose.id

            return JsonResponse({'status' : 'Appointment rebooked successfully', 'appointment' : appointment_dict}, status=200)

        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'Appointment not found'}, status=404)
        except ValueError:
            return JsonResponse({'status': 'Invalid data'}, status=400)
    else:
        return JsonResponse({'status': 'Invalid method'}, status=400)

@login_required
def check_if_full(request):
    if request.method == 'GET':
        selected_date_str = request.GET.get('selected_date')
        try:
            selected_date = datetime.strptime(selected_date_str.split('T')[0], "%Y-%m-%d").date()  
            num_appointments = Appointment.objects.filter(date=selected_date, status='pending', isActive=True).count()
            max_slots = MaximumAppointment.load().max_appointments
            date_slot = DateSlot.objects.filter(date=selected_date).first()
            max_morning_slots = date_slot.morning_slots if date_slot else (max_slots / 2)
            max_afternoon_slots = date_slot.afternoon_slots if date_slot else (max_slots / 2)

            total_slots = max_morning_slots + max_afternoon_slots

            doctor_schedule = DoctorSchedule.objects.filter(date=selected_date, isActive=True).first()

            if num_appointments >= total_slots:
                return JsonResponse({'status': 'full'}, status=200)
            elif num_appointments >= max_morning_slots:
                return JsonResponse({'status': 'morning_full'}, status=200)
            elif num_appointments >= max_afternoon_slots:
                return JsonResponse({'status': 'afternoon_full'}, status=200)
            elif doctor_schedule:
                if doctor_schedule.timeOfTheDay == 'morning':
                    return JsonResponse({'status': 'morning_full'}, status=200)
                elif doctor_schedule.timeOfTheDay == 'afternoon':
                    return JsonResponse({'status': 'afternoon_full'}, status=200)
            else:
                return JsonResponse({'status': 'not full'}, status=200)
        except ValueError:
            return JsonResponse({'status': 'Invalid date format'}, status=400)
    else:
        return JsonResponse({'status': 'Invalid method'}, status=400)

@login_required
@staff_required
def get_pets(request):
    try:
        client_id = request.GET.get('client_id')
        pets = Pet.objects.filter(client=client_id, is_active=True).values('id', 'name')
        return JsonResponse(list(pets), safe=False)
    except:
        return JsonResponse({'status': 'error', 'message': 'Client not found'})

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
            
            if appointment.status == 'done':
                return JsonResponse({'status': 'error', 'message': 'This appointment is already marked as done, please refresh the page.'}, status=400)
                
            appointment.status = 'done'
            appointment.isActive = False
            appointment.save()

            # get the appointment's date
            if appointment.date:
                appointment_date = appointment.date.strftime("%Y-%m-%d")
                return JsonResponse({'status': 'Appointment marked as done successfully.', 'appointment_date': appointment_date})
            else:
                return JsonResponse({'status': 'Appointment marked as done successfully.'})
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
@staff_required
def set_time_of_the_day(request):
    if request.method == 'POST':
        try:
            appointment_id = request.POST.get('appointment_id')

            appointment_date = Appointment.objects.get(id=appointment_id).date

            if appointment_date is None:
                return JsonResponse({'status': 'error', 'message': 'Please set the date of the appointment first.'}, status=400)
            
            disabled_day = DoctorSchedule.objects.filter(date=appointment_date, isActive=True).first() 

            if disabled_day:
                if disabled_day.timeOfTheDay == 'whole_day' or disabled_day.timeOfTheDay == time_of_the_day:
                    return JsonResponse({'status': 'error', 'message': 'The chosen time is disabled, please refresh the page.'}, status=400)

            new_time = request.POST.get('new_time')

            appointment = Appointment.objects.get(id=appointment_id)

            if new_time > '12:00:00' and new_time < '18:00:00':
                time_of_the_day = 'afternoon'
            else:
                time_of_the_day = 'morning'

            appointment.time = new_time
            appointment.timeOfTheDay = time_of_the_day
            appointment.save()

            new_time = appointment.time

            return JsonResponse({'status': 'success', 'message': 'Time of the day updated successfully.', 'new_time': new_time, 'date': appointment_date.strftime("%Y-%m-%d")})
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found.'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

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

    appointment_id = request.GET.get('appointment_id')
    appointment = None
    if appointment_id:
        try:
            appointment = Appointment.objects.get(id=appointment_id, isActive=True, client=client)
        except Appointment.DoesNotExist:
            pass

    today = datetime.now().date()
    today_date_slots = DateSlot.objects.filter(date=today, isActive=True).first()
    if today_date_slots is None:
        slotsAvailableToday = 0
    else:
        today_appointments = Appointment.objects.filter(date=today, isActive=True)

        slots_taken = sum(appointment.slots_taken for appointment in today_appointments)

        slotsAvailableToday = (today_date_slots.morning_slots + today_date_slots.afternoon_slots) - slots_taken

    change_time_form = ChangeTimeForm()

    context = {
        'form': form,
        'client': client,
        'rebook_appointments': rebook_appointments,
        'rebook_form': rebook_form,
        'appointment': appointment,
        'slotsAvailableToday': slotsAvailableToday,
        'change_time_form': change_time_form,
    }

    return render(request, 'client/calendar.html', context)

@login_required
@csrf_exempt
def set_appointment_client(request):
    if request.method == 'POST':
        try:
            pet_id = request.POST['pet']
            time = request.POST['time']
            iso_timestamp = request.POST['date']
            
            if time >= '12:00:00' and time < '18:00:00':
                time_of_day = 'afternoon'
            else:
                time_of_day = 'morning'

            datetime_object = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
            
            datetime_object = datetime_object.replace(tzinfo=timezone.utc).astimezone(timezone.get_current_timezone())

            date = datetime_object.date().isoformat()

            disabled_day = DoctorSchedule.objects.filter(date=date).first()
            if disabled_day and disabled_day.isActive and (disabled_day.timeOfTheDay == time_of_day or disabled_day.timeOfTheDay == 'whole_day'):
                return JsonResponse({'status': 'error', 'message': 'The chosen date and time is disabled for appointments'}, status=400)

            service_id = request.POST['purpose']
            service = Service.objects.get(pk=service_id)

            existing_appointment = Appointment.objects.filter(date=date, time=time, isActive=True).first()

            if existing_appointment:
                existing_service = existing_appointment.purpose
                if existing_service.job_for == 'doctor' and service.job_for == 'doctor':
                    return JsonResponse({'status': 'error', 'message': 'A doctor is already booked for a service at this time.'}, status=400)

            status = 'pending'

            date_slot = DateSlot.objects.filter(date=date).first()
            maximum_appointments = MaximumAppointment.load()
            doctor_schedule = DoctorSchedule.objects.filter(date=date, isActive=True).first()

            if date_slot:
                if time_of_day == 'morning':
                    morning_slots_remaining = date_slot.morning_slots - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='morning').count()
                    
                    print(morning_slots_remaining)

                    if morning_slots_remaining != 1:
                        morning_slots_remaining -= 1

                    if morning_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for morning on this date.'}, status=400)
                elif time_of_day == 'afternoon':
                    afternoon_slots_remaining = date_slot.afternoon_slots - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                    if afternoon_slots_remaining != 1:
                        afternoon_slots_remaining -= 1
                    
                    print(afternoon_slots_remaining)

                    if afternoon_slots_remaining <= 0:
                        return JsonResponse({'status': 'error', 'message': 'No more slots available for afternoon on this date.'}, status=400)
            else:
                if doctor_schedule:
                    if doctor_schedule.timeOfTheDay == 'afternoon' and time_of_day == 'morning':
                        
                        morning_slots_remaining = maximum_appointments.max_appointments // 2 - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='morning').count()

                        if morning_slots_remaining != 1:
                            morning_slots_remaining -= 1
                        
                        if morning_slots_remaining <= 0:
                            return JsonResponse({'status': 'error', 'message': 'No more slots available for morning on this date.'}, status=400)

                    elif doctor_schedule.timeOfTheDay == 'morning' and time_of_day == 'afternoon':
                        
                        afternoon_slots_remaining = maximum_appointments.max_appointments // 2 - Appointment.objects.filter(date=date, isActive=True, status='pending', timeOfTheDay='afternoon').count()
                        
                        if afternoon_slots_remaining != 1:
                            afternoon_slots_remaining -= 1
                        
                        if afternoon_slots_remaining <= 0:
                            return JsonResponse({'status': 'error', 'message': 'No more slots available for afternoon on this date.'}, status=400)

                if Appointment.objects.filter(date=date, isActive=True, status='pending').count() >= maximum_appointments.max_appointments:
                    return JsonResponse({'status': 'error', 'message': 'No more slots available for this date.'}, status=400)

            existing_appointment = Appointment.objects.filter(pet_id=pet_id, status__in=["pending", "rebook"], isActive=True).first()
            if existing_appointment:
                return JsonResponse({'status': 'error', 'message': 'This pet already has an appointment, please refresh the page.'}, status=400)

            appointment = Appointment(client_id=request.user.client.id, pet_id=pet_id, timeOfTheDay=time_of_day, 
                                      date=date, time=time, purpose_id=service_id, status=status, isActive=True)
               
            appointment.save()
            
            appointment_dict = model_to_dict(appointment)

            appointment_dict['pet'] = model_to_dict(appointment.pet, exclude=['picture'])
            appointment_dict['client'] = model_to_dict(appointment.client)
            appointment_dict['color'] = appointment.getTimeOfDayColor()
            appointment_dict['timeOfTheDay'] = appointment.get_timeOfTheDay_display()
            appointment_dict['timeOfTheDay_val'] = appointment.timeOfTheDay
            appointment_dict['time'] = appointment.time
            appointment_dict['purpose'] = appointment.purpose.service_type
            appointment_dict['purpose_id'] = appointment.purpose.id
 
            return JsonResponse({'message': 'Appointment created successfully', 'appointment': appointment_dict})
        except MultiValueDictKeyError:
            return JsonResponse({'error': 'One of the required keys is missing from the form data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

# @login_required
# def get_appointments_client(request):
#     appointments = Appointment.objects.filter(client=request.user.client, status='pending', isActive=True, pet__is_active=True).order_by('-timeOfTheDay')

#     event_list = []
#     for appointment in appointments:
#         event = {
#             'id': appointment.id,
#             #'title': f'#{appointment.id} - {appointment.pet.name}',
#             'title': f'{appointment.pet.name}',
#             'start': appointment.date.isoformat(),
#             'color': appointment.getTimeOfDayColor(),
#             'extendedProps': {
#                 'client_id': appointment.client.id,
#                 'client': appointment.client.full_name,
#                 'contact_number': appointment.client.contact_number,
#                 'pet': appointment.pet.name,  
#                 'pet_id': appointment.pet.id,
#                 'timeOfTheDay': appointment.get_timeOfTheDay_display(),
#                 'timeOfTheDay_val': appointment.timeOfTheDay,
#                 'purpose': appointment.purpose.service_type,
#                 'purpose_id': appointment.purpose.id,
#                 'current_date': appointment.date.isoformat(),
#                 'day_sms_reminder': appointment.daily_reminder_sent,
#                 'week_sms_reminder': appointment.weekly_reminder_sent,
#             }
#         }
#         event_list.append(event)

#     return JsonResponse(event_list, safe=False)

@login_required
def is_all_my_pets_scheduled(request):
    client_pets = Pet.objects.filter(client=request.user.client, is_active=True)
    pets_with_appointments = Appointment.objects.exclude(status='cancelled').filter(pet__in=client_pets, status__in=['pending', 'rebook'], isActive=True).values_list('pet', flat=True).distinct()

    if client_pets.count() == pets_with_appointments.count():
        return JsonResponse({'all_scheduled': True})
    else:
        return JsonResponse({'all_scheduled': False})

# @login_required
# def get_appointments_count(request):
#     appointments = Appointment.objects.filter(status__in=['pending', 'rebook'])
#     appointment_counts = {}
#     for appointment in appointments:
#         date_str = appointment.date.strftime('%Y-%m-%d')
#         if date_str in appointment_counts:
#             appointment_counts[date_str] += 1
#         else:
#             appointment_counts[date_str] = 1

#     return JsonResponse(appointment_counts)

@login_required
def get_pets_client(request):
    client_id = request.GET.get('client_id')
    selected_pet_id = request.GET.get('selected_pet_id')

    pets_with_appointments = Appointment.objects.exclude(
        status__in=['cancelled', 'done']).filter(pet__client=client_id, isActive=True).values_list('pet', flat=True)
    
    pets_without_appointments = Pet.objects.filter(client=client_id, is_active=True).exclude(id__in=pets_with_appointments).values('id', 'name')
    selected_pet = Pet.objects.filter(id=selected_pet_id, is_active=True).values('id', 'name')

    pets = pets_without_appointments | selected_pet
    #print(list(pets))
    return JsonResponse(list(pets), safe=False)

@login_required
@staff_required
def get_all_data(request):
    # Get appointments
    appointments = Appointment.objects.filter(status='pending', isActive=True, pet__is_active=True).order_by('time')
    event_list = []
    
    for appointment in appointments:
        event = {
            'id': appointment.id,
            'title': f'{appointment.client.full_name}',
            'start': f'{appointment.date.isoformat()}T{appointment.time}',
            'end': f'{appointment.date.isoformat()}T{appointment.time}',
            'color': appointment.getTimeOfDayColor(),
            'allDay': False,
            'extendedProps': {
                'client_id': appointment.client.id,
                'client': appointment.client.full_name,
                'contact_number': appointment.client.contact_number,
                'pet': appointment.pet.name,  
                'pet_id': appointment.pet.id,
                'timeOfTheDay': appointment.get_timeOfTheDay_display(),
                'timeOfTheDay_val': appointment.timeOfTheDay,
                'time': appointment.time,
                'purpose': appointment.purpose.service_type if appointment.purpose else None,
                'purpose_id': appointment.purpose.id if appointment.purpose else None,
                'current_date': appointment.date.isoformat() if appointment.date is not None else '',
                'day_sms_reminder': appointment.daily_reminder_sent,
                'week_sms_reminder': appointment.weekly_reminder_sent,
            }
        }
        event_list.append(event)

    # Get disabled days
    disabled_days = DoctorSchedule.objects.filter(isActive=True).values('date', 'timeOfTheDay')
    disabled_days_list = list(disabled_days)

    # Get max appointments
    max_appointments = MaximumAppointment.load()

    # Get date slots
    date_slots = DateSlot.objects.filter(isActive=True).values('date', 'morning_slots', 'afternoon_slots')
    date_slots_list = list(date_slots)

    all_pets = Pet.objects.filter(is_active=True).values('id', 'client__id')
    all_clients = Client.objects.filter(user__is_active=True, isBanned=False).values('id')

    # Construct response data
    data = {
        'appointments': event_list,
        'disabled_days': disabled_days_list,
        'max_appointments': max_appointments.max_appointments,
        'date_slots': date_slots_list,
        'all_pets': list(all_pets),
        'all_clients': list(all_clients),
    }

    return JsonResponse(data, safe=False)

@login_required
def get_all_data_client(request):
    # Get appointments count
    appointments = Appointment.objects.filter(status='pending', isActive=True)
    appointment_counts = {}
    morning_appointment_counts = {}
    afternoon_appointment_counts = {}
    for appointment in appointments:
        date_str = appointment.date.strftime('%Y-%m-%d')
        if date_str in appointment_counts:
            appointment_counts[date_str] += 1
        else:
            appointment_counts[date_str] = 1

        if appointment.timeOfTheDay == 'morning':
            date_str = appointment.date.strftime('%Y-%m-%d')
            if date_str in morning_appointment_counts:
                morning_appointment_counts[date_str] += 1
            else:
                morning_appointment_counts[date_str] = 1
        elif appointment.timeOfTheDay == 'afternoon':
            date_str = appointment.date.strftime('%Y-%m-%d')
            if date_str in afternoon_appointment_counts:
                afternoon_appointment_counts[date_str] += 1
            else:
                afternoon_appointment_counts[date_str] = 1

    # Get appointments
    appointments = Appointment.objects.filter(client=request.user.client, status__in=['pending'], isActive=True, pet__is_active=True).order_by('time')
    event_list = []
    for appointment in appointments:
        event = {
            'id': appointment.id,
            'title': f'{appointment.pet.name}',
            'start': f'{appointment.date.isoformat()}T{appointment.time}',
            'color': appointment.getTimeOfDayColor(),
            'allDay': False,
            'extendedProps': {
                'client_id': appointment.client.id,
                'client': appointment.client.full_name,
                'contact_number': appointment.client.contact_number,
                'pet': appointment.pet.name,  
                'pet_id': appointment.pet.id,
                'timeOfTheDay': appointment.get_timeOfTheDay_display(),
                'timeOfTheDay_val': appointment.timeOfTheDay,
                'time': appointment.time,
                'purpose': appointment.purpose.service_type if appointment.purpose else None,
                'purpose_id': appointment.purpose.id if appointment.purpose else None,
                'current_date': appointment.date.isoformat(),
                'day_sms_reminder': appointment.daily_reminder_sent,
                'week_sms_reminder': appointment.weekly_reminder_sent,
            }
        }
        event_list.append(event)

    print(event_list)

    # Get disabled days
    disabled_days = DoctorSchedule.objects.filter(isActive=True).values('date', 'timeOfTheDay')
    disabled_days_list = list(disabled_days)

    # Get max appointments
    max_appointments = MaximumAppointment.load()

    # Get date slots
    date_slots = DateSlot.objects.filter(isActive=True).values('date', 'morning_slots', 'afternoon_slots')
    date_slots_list = list(date_slots)

    # Check if all pets are scheduled
    client_pets = Pet.objects.filter(client=request.user.client, is_active=True)
    pets_with_appointments = Appointment.objects.exclude(status='cancelled').filter(pet__in=client_pets, status__in=['pending', 'rebook'], isActive=True).values_list('pet', flat=True).distinct()

    if client_pets.count() == pets_with_appointments.count():
        all_scheduled = True
    else:
        all_scheduled = False

    # Get my pets
    my_pets = Pet.objects.filter(client=request.user.client, is_active=True).values('id', 'name')

    # Construct response data
    data = {
        'appointment_counts': appointment_counts,
        'morning_appointment_counts': morning_appointment_counts,
        'afternoon_appointment_counts': afternoon_appointment_counts,
        'appointments': event_list,
        'disabled_days': disabled_days_list,
        'max_appointments': max_appointments.max_appointments,
        'date_slots': date_slots_list,
        'all_scheduled': all_scheduled,
        'my_pets': list(my_pets),
    }

    return JsonResponse(data, safe=False)

@login_required
def client_set_time_of_the_day(request, client_id):
    if request.method == 'POST':
        try:
            client = Client.objects.get(id=client_id)

            if client.user != request.user:
                return JsonResponse({'status': 'error', 'message': 'You are not authorized to perform this action.'}, status=403)

            appointment_id = request.POST.get('appointment_id')

            appointment_date = Appointment.objects.get(id=appointment_id, client=client_id).date

            if appointment_date is None:
                return JsonResponse({'status': 'error', 'message': 'Please set the date of the appointment first.'}, status=400)
            
            disabled_day = DoctorSchedule.objects.filter(date=appointment_date, isActive=True).first() 

            if disabled_day:
                if disabled_day.timeOfTheDay == 'whole_day' or disabled_day.timeOfTheDay == time_of_the_day:
                    return JsonResponse({'status': 'error', 'message': 'The chosen time is disabled, please refresh the page.'}, status=400)

            new_time = request.POST.get('new_time')

            appointment = Appointment.objects.get(id=appointment_id, client=client_id)

            if not appointment:
                return JsonResponse({'status': 'error', 'message': 'Appointment not found, or you are not the owner.'}, status=404)

            if new_time > '12:00:00' and new_time < '18:00:00':
                time_of_the_day = 'afternoon'
            else:
                time_of_the_day = 'morning'

            appointment.time = new_time
            appointment.timeOfTheDay = time_of_the_day
            appointment.save()

            new_time = appointment.time

            return JsonResponse({'status': 'success', 'message': 'Time of the day updated successfully.', 'new_time': new_time, 'date': appointment_date.strftime("%Y-%m-%d")})
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found.'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)