# ----------------------------------------------IMPORTS--------------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    login,
    logout,
    authenticate,
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import json
import time
import imghdr

from .forms import *
from .models import (
    Client,
    Pet,
    PetMedicalPrescription,
    PrescriptionMedicines,
    PetTreatment,
    TemporaryLabResultImage,
    LabResult,
    LabResultsTreatment,
    TreatmentCycle
)

from django.contrib.auth import login, logout
from core.semaphore import send_sms, send_otp_sms
from core.decorators import staff_required
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q

from appointment_management.models import (
    Appointment,
    MaximumAppointment,
    DateSlot,
    DoctorSchedule,
)
from inventory.models import Product, ProductType
from services.models import Service

from django.conf import settings

from django.core.serializers import serialize

from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ConsultationSerializer, TemporaryLabResultImageSerializer, PrescriptionSerializer, HealthCardSerializer, UpdateConsultationSerializer


OTP_EXPIRATION_MINUTE = settings.OTP_EXPIRATION_MINUTES
#-------------------------------------------------------------------------------------------------------------
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = PasswordResetStep1(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                client = user.client
                phone_number = client.contact_number
                otp_code = send_otp_sms(phone_number)

                request.session['otp_code'] = otp_code
                request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTE)).timestamp()
                request.session['temp_user_id'] = user.id
                request.session['temp_user_session'] = request.session.session_key
                request.session['otp_attempt_count'] = 0
                request.session['otp_context'] = 'password_reset'
                request.session.save()

                return redirect('otp_view')
            except User.DoesNotExist:
                messages.error(request, 'User with this username does not exist.')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordResetStep1()
    return render(request, 'client/forgot_password.html', {'form': form})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        username = request.POST.get('username', '') 
        password = request.POST.get('password', '')

        client_ip = get_client_ip(request)
        attempts_key = f'attempts_{client_ip}'
        attempts = cache.get(attempts_key, 0)

        if attempts >= 2:
            messages.error(request, 'Too many attempts. Please try again after 2 minutes.')
            return render(request, 'client/login.html', {'form': form})

        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                phone_number = user.client.contact_number
                otp_code = send_otp_sms(phone_number)
                request.session['otp_code'] = otp_code
                request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTE)).timestamp()
                request.session['temp_user_id'] = user.id
                request.session['temp_user_session'] = request.session.session_key
                request.session['otp_attempt_count'] = 0
                request.session.save()

                return redirect('otp_view')

            if not user.client.two_auth_enabled:
                login(request, user)
                cache.set(attempts_key, 0, 2 * 60)
                if not user.is_staff:
                    return redirect('customer-dashboard')
                return redirect('home')

            phone_number = user.client.contact_number
            otp_code = send_otp_sms(phone_number)

            request.session['otp_code'] = otp_code
            request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTE)).timestamp()
            request.session['temp_user_id'] = user.id
            request.session['temp_user_session'] = request.session.session_key
            request.session['otp_attempt_count'] = 0
            request.session.save()
            
            cache.set(attempts_key, 0, 2 * 60)

            return redirect('otp_view')
        else:
            cache.set(attempts_key, attempts + 1, 2 * 60)  
    else:
        form = LoginForm()
    return render(request, 'client/login.html', {'form': form})

def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                client = Client(
                    user=user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    gender=form.cleaned_data['gender'],
                    street=form.cleaned_data['street'],
                    barangay=form.cleaned_data['barangay'],
                    city=form.cleaned_data['city'],
                    province=form.cleaned_data['province'],
                    contact_number=form.cleaned_data['contact_number']
                )
                client.save()

            phone_number = client.contact_number
            otp_code = send_otp_sms(phone_number)

            request.session['otp_code'] = otp_code
            request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTE)).timestamp()
            request.session['temp_user_id'] = user.id
            request.session['temp_user_session'] = request.session.session_key
            request.session['otp_attempt_count'] = 0
            request.session.save()

            return redirect('otp_view')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'client/client_register.html', context)

@login_required
def client_profile_view(request):
    user = request.user
    client = get_object_or_404(Client, user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        client_form = ClientUpdateForm(request.POST, instance=client)

        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            client_form.save()
            return redirect('client-account-settings-page')
        # else:
        #     print(user_form.errors) 
        #     print(client_form.errors)
    else:
        user_form = UserUpdateForm(instance=user)
        client_form = ClientUpdateForm(instance=client)

    context = {'user_form': user_form, 'client_form': client_form}

    return render(request, 'client/client_account_settings.html', context)

@login_required
def client_change_password_view(request):
    if request.method == 'POST':
        password_form = AdminChangePasswordForm(user=request.user, data=request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!', extra_tags='password_form')
            return redirect('client-password-settings-page')
        else:
            messages.error(request, 'Please correct the error below.')
                 
    else:
        password_form = AdminChangePasswordForm(user=request.user)
        
    return render(request, 'client/client_password_settings.html', {'password_form': password_form})

@login_required
def client_change_otp_view(request):
    if request.method == 'POST':
        two_factor_form = TwoFactorAuthenticationForm(request.POST)

        if two_factor_form.is_valid():
            client = request.user.client
            client.two_auth_enabled = two_factor_form.cleaned_data['two_auth_enabled']
            client.save()
            messages.success(request, 'Two-factor authentication settings successfully updated!')
            return redirect('client-otp-settings-page')
        else:
            messages.error(request, 'Please correct the error below.')  
    else:
        two_factor_form = TwoFactorAuthenticationForm(initial={'two_auth_enabled': request.user.client.two_auth_enabled})
        
    return render(request, 'client/client_otp_settings.html', {'two_factor_form': two_factor_form, 'sms_number': request.user.client.contact_number})

@csrf_exempt
def otp_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    # user_session = request.session.get('temp_user_session')

    # if user_session != request.session.session_key:
    #     return redirect('home')

    otp_context = request.session.get('otp_context', None)
    otp_expiration_timestamp = request.session.get('otp_code_expiration', 0)
    time_remaining = max(0, int(otp_expiration_timestamp - datetime.now().timestamp()))
    user_id = request.session.get('temp_user_id')

    if not user_id:
        return redirect('home')

    otp_expired = False
    attempt_limit = 3 

    if datetime.now().timestamp() > otp_expiration_timestamp:
        del request.session['temp_user_id']
        del request.session['otp_code']
        del request.session['otp_code_expiration']
        del request.session['temp_user_session']
        del request.session['otp_attempt_count']

        return redirect('home')

    if request.method == 'POST':
        entered_otp_code = int(request.POST.get('otp_code'))
        stored_otp_code = int(request.session.get('otp_code', None))
        attempt_count = request.session.get('otp_attempt_count', 0)

        if datetime.now().timestamp() > otp_expiration_timestamp:
            otp_expired = True
            return render(request, 'client/otp.html', {'error_message': 'Expired OTP. Please try again.', 'time_remaining': time_remaining, 'otp_expired': otp_expired})

        if entered_otp_code != stored_otp_code:
            attempt_count += 1
            request.session['otp_attempt_count'] = attempt_count

            if attempt_count >= attempt_limit:
                del request.session['temp_user_id']
                del request.session['otp_code']
                del request.session['otp_code_expiration']
                del request.session['temp_user_session']
                del request.session['otp_attempt_count']

                return redirect('home')

            remaining_attempts = attempt_limit - attempt_count
            return render(request, 'client/otp.html', {'error_message': f'Invalid OTP. Please try again. Attempts ({attempt_count}/{attempt_limit})', 'time_remaining': time_remaining, 'remaining_attempts': remaining_attempts})

        if entered_otp_code == stored_otp_code:
            if user_id:
                if otp_context == 'password_reset':
                    del request.session['otp_code'] 
                    del request.session['otp_code_expiration'] 
                    del request.session['temp_user_session']
                    del request.session['otp_attempt_count']

                    return redirect('forgot-password-step-3-page')
                else:
                    user = User.objects.get(id=user_id)
                    user.is_active = True
                    user.save()
                    
                    login(request, user)

                    del request.session['temp_user_id']
                    del request.session['otp_code']
                    del request.session['otp_code_expiration']
                    del request.session['temp_user_session']

                    if 'otp_attempt_count' in request.session:
                        del request.session['otp_attempt_count']
                
                    return redirect('home')
            else:
                return HttpResponse("An error occurred. Please try again.")
        else:
            if user_id:
                user = User.objects.get(id=user_id)
                user.delete()
            return HttpResponse("Invalid OTP. Please try again.")
    else:
        if user_id:
            user = User.objects.get(id=user_id)
            contact_number = user.client.contact_number
            return render(request, 'client/otp.html', {'contact_number': contact_number, 'time_remaining': time_remaining})
        else:
            return HttpResponse("An error occurred. Please try again.")

def forgot_password_step_3(request):
    if request.user.is_authenticated:
        return redirect('home')

    user_id = request.session.get('temp_user_id')

    if not user_id:
        messages.error(request, 'There was an error. You might skipped a step.')
        return redirect('forgot-password-page')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('forgot-password-page')

    if request.method == 'POST':
        form = PasswordResetStep2(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            confirm_new_password = form.cleaned_data.get('confirm_new_password')

            if new_password != confirm_new_password:
                messages.error(request, 'Passwords do not match. Please try again.')
                return render(request, 'client/forgot_password_step3.html', {'form': form})

            user.set_password(new_password)
            user.save()

            del request.session['temp_user_id']
            del request.session['otp_context']

            messages.success(request, 'Password changed successfully. Please login with your new password.')
            return redirect('login-page')

        else:
            messages.error(request, 'Please fill out the form correctly.')
            return render(request, 'client/forgot_password_step3.html', {'form': form})

    else:
        form = PasswordResetStep2()

    return render(request, 'client/forgot_password_step3.html', {'form': form})

@csrf_exempt
def resend_otp(request):
    if request.user.is_authenticated:
        return redirect('home')

    user_id = request.session.get('temp_user_id')

    if user_id:
        user = User.objects.get(id=user_id)
        phone_number = user.client.contact_number
        otp_code = send_otp_sms(phone_number)

        if 'otp_code' in request.session:
            del request.session['otp_code']
        if 'otp_code_expiration' in request.session:
            del request.session['otp_code_expiration']
        if 'otp_attempt_count' in request.session:
            del request.session['otp_attempt_count']

        request.session['otp_code'] = otp_code
        request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTE)).timestamp()
        request.session['otp_attempt_count'] = 0

        return redirect('otp_view')
    else:
        return redirect('home')

@login_required
@transaction.atomic 
def register_pet(request):
    if request.method == 'POST':
        form = PetRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.client = request.user.client
            
            if not pet.id: 
                pet.original_weight = pet.weight
            else:
                pet_in_db = Pet.objects.select_for_update().get(id=pet.id)
                if pet_in_db.original_weight is not None:
                    pet.original_weight = pet_in_db.original_weight

            pet.save()
            return redirect('pet-list-page')
    else:
        form = PetRegistrationForm()

    context = {'form': form}
    return render(request, 'client/pet_register.html', context)

@login_required
def view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    appointment = Appointment.objects.filter(pet=pet, client=request.user.client, isActive=True).order_by('-id').first()

    if pet.client != request.user.client:
        return redirect('pet-list-page')

    pet_treatment = PetTreatment.objects.select_related('appointment').prefetch_related('petmedicalprescription').filter(pet=pet, isVaccine=False, isDeworm=False).order_by('-id')

    deworming_health_card = PetTreatment.objects.select_related('appointment').filter(pet=pet, isDeworm=True).order_by('-id')
    vaccination_health_card = PetTreatment.objects.select_related('appointment').filter(pet=pet, isVaccine=True).order_by('-id')


    context = {
        'pet': pet, 'appointment': appointment,
        'pet_treatment': pet_treatment,
        'deworming_health_card': deworming_health_card,
        'vaccination_health_card': vaccination_health_card
    }
    return render(request, 'client/view_pet.html', context)

@login_required
def update_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if pet.client != request.user.client:
        return redirect('pet-list-page')

    if request.method == 'POST':
        form = PetRegistrationForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('view-pet-page', pet_id=pet.id)
    else:
        form = PetRegistrationForm(instance=pet)
    
    context = {'form': form, 'pet': pet}
    return render(request, 'client/update_pet.html', context)

# ? This is the old delete pet function
# ? @login_required
# ? def delete_pet(request, pet_id):
# ?     pet = get_object_or_404(Pet, id=pet_id)
    
# ?     if pet.client != request.user.client:
# ?         return redirect('pet-list-page')

# ?     if request.method == 'POST':
# ?         #set is_active to False
# ?         pet.is_active = False
# ?         pet.save()
# ?         return JsonResponse({'result': 'success'})
# ?     else:
# ?         return JsonResponse({'result': 'error', 'message': 'Invalid request method'})

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
    if pet.client != request.user.client:
        return redirect('pet-list-page')

    if request.method == 'POST':
        #set pet as inactive
        pet.is_active = False
        pet.save()

        appointments = Appointment.objects.filter(pet=pet)
        if appointments:
            for appointment in appointments:
                appointment.status = 'cancelled'
                appointment.isActive = False
                appointment.save()

        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})

@login_required
def pet_list(request):
    pets = Pet.objects.filter(client=request.user.client, is_active=True).order_by('-id')
    for pet in pets:
        pet.has_active_appointment = pet.appointment_set.filter(isActive=True, pet=pet)
        if pet.has_active_appointment.exists():
            pet.active_appointment_id = pet.has_active_appointment.first().id
    context = {'pets': pets}
    return render(request, 'client/pet_list.html', context)


@login_required
def does_pet_have_appointment(request, pet_id):
    has_appointment = Appointment.objects.filter(pet_id=pet_id, status__in=['pending', 'rebook'], isActive=True).exclude(status='cancelled').exists()
    return JsonResponse({'has_appointment': has_appointment})

#--------------------ADMIN-SIDE-BACKEND--------------------
from django.db.models import Count

@login_required
@staff_required
def admin_profile_view(request):
    user = request.user
    client = get_object_or_404(Client, user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        client_form = ClientUpdateForm(request.POST, instance=client)

        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            client_form.save()
            return redirect('admin-account-settings-page')
    else:
        user_form = UserUpdateForm(instance=user)
        client_form = ClientUpdateForm(instance=client)

    context = {'user_form': user_form, 'client_form': client_form}

    return render(request, 'admin/admin_account_settings.html', context)

@login_required
@staff_required
def admin_change_password_view(request):
    if request.method == 'POST':
        password_form = AdminChangePasswordForm(user=request.user, data=request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!', extra_tags='password_form')
            return redirect('admin-password-settings-page')
        else:
            messages.error(request, 'Please correct the error below.')
                 
    else:
        password_form = AdminChangePasswordForm(user=request.user)
        
    return render(request, 'admin/admin_password_settings.html', {'password_form': password_form})

@login_required
@staff_required
def admin_change_otp_view(request):
    if request.method == 'POST':
        two_factor_form = TwoFactorAuthenticationForm(request.POST)

        if two_factor_form.is_valid():
            client = request.user.client
            client.two_auth_enabled = two_factor_form.cleaned_data['two_auth_enabled']
            client.save()
            messages.success(request, 'Two-factor authentication settings successfully updated!')
            return redirect('admin-otp-settings-page')
        else:
            messages.error(request, 'Please correct the error below.')  
    else:
        two_factor_form = TwoFactorAuthenticationForm(initial={'two_auth_enabled': request.user.client.two_auth_enabled})
        
    return render(request, 'admin/admin_otp_settings.html', {'two_factor_form': two_factor_form, 'sms_number': request.user.client.contact_number})

@staff_required
@login_required
def client_module(request):
    clients = Client.objects.filter(user__is_active=True).annotate(total_pets=Count('pet')).order_by('-id')
    context = {'clients': clients}
    return render(request, 'admin/client_module.html', context)

@staff_required
@login_required
def admin_view_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    pets = client.pet_set.all()

    context = {'client': client, 'pets': pets}
    return render(request, 'admin/view_client.html', context)

@staff_required
@login_required
def pet_module(request):
    pets = Pet.objects.all().order_by('-id')
    context = {'pets': pets}
    return render(request, 'admin/pet_module/pet_module.html', context)

@staff_required
@login_required
def admin_view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    pet_treatment = PetTreatment.objects.select_related('appointment').prefetch_related('petmedicalprescription').filter(pet=pet, isVaccine=False, isDeworm=False).order_by('-id')

    deworming_health_card = PetTreatment.objects.select_related('appointment').prefetch_related('petmedicalprescription').filter(pet=pet, isDeworm=True).order_by('-id')
    vaccination_health_card = PetTreatment.objects.select_related('appointment').prefetch_related('petmedicalprescription').filter(pet=pet, isVaccine=True).order_by('-id')

    inactive_pet_treatment = PetTreatment.objects.select_related('appointment').prefetch_related('petmedicalprescription').filter(pet=pet, isVaccine=False, isDeworm=False, isActive=False).order_by('-id')

    inactive_health_card = PetTreatment.objects.select_related('appointment')\
        .prefetch_related('petmedicalprescription')\
        .filter(
            Q(isDeworm=True) | Q(isVaccine=True),
            pet=pet,
            isActive=False
        )\
        .order_by('-id')

    context = {
        'pet': pet,
        'pet_treatment': pet_treatment,
        'deworming_health_card': deworming_health_card,
        'vaccination_health_card': vaccination_health_card,
        'inactive_pet_treatment': inactive_pet_treatment,
        'inactive_health_card': inactive_health_card
    }
    return render(request, 'admin/pet_module/view_pet.html', context)


@staff_required
@login_required
def admin_update_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == 'POST':
        form = AdminPetRegistrationForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('admin-view-pet-page', pet_id=pet.id)
    else:
        form = AdminPetRegistrationForm(instance=pet)
    
    context = {'form': form, 'pet': pet}
    return render(request, 'admin/pet_module/update_pet.html', context)

@staff_required
@login_required
def medical_record(request):
    pets = Pet.objects.filter(is_active=True).order_by('-id')
    types = ProductType.objects.filter(name="Medicines")

    product_dict = {}
    for t in types:
        products = Product.objects.filter(type=t, active=True)
        filtered_products = [product for product in products if not product.is_product_expired() and not product.is_product_out_of_stock()]
        product_dict[t.name] = filtered_products

    formList = PrescriptionMedicines.MEDICINES_FORM_LIST

    services = Service.objects.filter(active=True)

    all_appointments = Appointment.objects.filter(isActive=True, status='pending').order_by('-id')
    max_appointment = MaximumAppointment.objects.first()
    date_slots = DateSlot.objects.all()
    doctor_schedules = DoctorSchedule.objects.all()

    all_appointments = serialize('json', all_appointments)
    date_slots = serialize('json', date_slots)
    doctor_schedules = serialize('json', doctor_schedules)

    context = {
        'pets': pets, 
        'product_dict': product_dict, 
        'formList': formList,
        'services': services ,
        'all_appointments': all_appointments,
        'max_appointment': max_appointment,
        'date_slots': date_slots,
        'doctor_schedules': doctor_schedules
    }
    return render(request, 'admin/consultation_module/consultation_module.html', context)

# @staff_required
# @login_required
# def submit_consultation(request):
#     if request.method == 'POST':
#         selected_pet_id = request.POST.get('selectedPetId')

#         appointment_date = request.POST.get('appointment_date')

#         if appointment_date:
#             #appointment_date = "Sep 21, 2023"
#             appointment_date_obj = datetime.strptime(appointment_date, '%b %d, %Y').date()
            
#             if appointment_date_obj < date.today():
#                 return JsonResponse({'success': False, 'appointment_error': True, 'message': 'Selected date is in the past.'})

#             doctor_schedule_for_date = DoctorSchedule.objects.filter(date=appointment_date_obj).first()

#             if doctor_schedule_for_date and doctor_schedule_for_date.timeOfTheDay == "whole_day":
#                 return JsonResponse({'success': False, 'appointment_error': True, 'message': 'Doctor is not available the whole day on the selected date.'})
            
#             appointment_time_of_the_day = request.POST.get('appointment_time_of_the_day')

#             if doctor_schedule_for_date and doctor_schedule_for_date.timeOfTheDay == appointment_time_of_the_day:
#                 return JsonResponse({'success': False, 'appointment_error': True, 'message': f'Doctor is not available in the {appointment_time_of_the_day} on the selected date.'})

#             appointments_for_date = Appointment.objects.filter(date=appointment_date_obj, isActive=True, status='pending').count()
#             date_slot = DateSlot.objects.filter(date=appointment_date_obj).first()
#             max_appointment = MaximumAppointment.objects.first().max_appointments

#             if date_slot:
#                 max_allowed = date_slot.slots
#             else:
#                 max_allowed = max_appointment
#             if appointments_for_date >= max_allowed:
#                 return JsonResponse({'success': False, 'appointment_error': True, 'message': 'No available slots on the selected date.'})

#         lab_results = request.POST.get('lab_results')
#         temperature = request.POST.get('temperature')
#         weight = request.POST.get('weight')
#         diagnosis = request.POST.get('diagnosis')
#         treatment = request.POST.get('treatment')
#         med_images = request.FILES.get('med_images')

#         is_deworm = True if request.POST.get('isDeworming') == 'true' else False
#         is_vaccine = True if request.POST.get('isVaccination') == 'true' else False

#         if med_images:
#             image_type = imghdr.what(med_images)
#             if image_type not in ["jpeg", "png", "jpg", "webp"]:
#                 return JsonResponse({'success': False, 'message': 'Invalid file type. Only .jpg, .jpeg, .png, and .webp files are allowed.'})

#         products_selected = request.POST.get('productsSelected')
#         if products_selected:
#             products_selected = json.loads(products_selected)

#         try:
#             with transaction.atomic():
#                 selected_pet = Pet.objects.get(pk=selected_pet_id)

#                 appointment = None

#                 if appointment_date:
#                     appointment_date_obj = datetime.strptime(appointment_date, '%b %d, %Y').date()
#                     appointment_time_of_the_day = request.POST.get('appointment_time_of_the_day')
#                     appointment_purpose = request.POST.get('appointment_purpose')

#                     selected_purpose = Service.objects.get(pk=appointment_purpose)

#                     appointment = Appointment.objects.create(
#                         pet=selected_pet,
#                         client=selected_pet.client,
#                         date=appointment_date_obj,
#                         timeOfTheDay=appointment_time_of_the_day,
#                         purpose=selected_purpose,
#                         status='pending',
#                         isActive=True
#                     )

#                 pet_treatment = PetTreatment.objects.create(
#                     pet_id=selected_pet.id,
#                     treatment_date=datetime.now(),
#                     lab_results=lab_results,
#                     treatment_weight=weight,
#                     temperature=temperature,
#                     diagnosis=diagnosis,
#                     treatment=treatment,
#                     appointment=appointment if appointment else None,
#                     medical_images=med_images,
#                     isDeworm=is_deworm,
#                     isVaccine=is_vaccine,
#                     isActive=True
#                 )

#                 if weight:
#                     selected_pet.weight = weight
#                     selected_pet.save()

#                 if products_selected:
#                     pet_medical_prescription = PetMedicalPrescription.objects.create(
#                         pet_id=selected_pet.id,
#                         date_prescribed=datetime.now(),
#                         pet_treatment=pet_treatment,
#                         isActive=True
#                     )

#                     for product_id, product_details in products_selected:
#                         PrescriptionMedicines.objects.create(
#                             prescription=pet_medical_prescription,
#                             medicine_id=product_id,
#                             strength=product_details['strength'],
#                             #form=product_details['form'],
#                             quantity=product_details['quantity'],
#                             dosage=product_details['dosage'],
#                             frequency=product_details['frequency'],
#                             remarks=product_details['remarks']
#                         )

#                 return JsonResponse({'success': True, 'message': 'Consultation submitted successfully.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)})
#     else:
#         return JsonResponse({'success': False, 'message': 'Invalid request method'})

@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class SubmitConsultationView(APIView):

    throttle_scope = 'submit_consultation'

    def post(self, request, *args, **kwargs):
        serializer = ConsultationSerializer(data=request.data)
        #print(serializer)

        if serializer.is_valid():
            selected_pet_id = serializer.validated_data.get('selectedPetId')
            appointment_date = serializer.validated_data.get('appointment_date')
            appointment_time_of_the_day = serializer.validated_data.get('appointment_time_of_the_day')
            appointment_purpose = serializer.validated_data.get('appointment_purpose')
            symptoms = serializer.validated_data.get('symptoms')
            temperature = serializer.validated_data.get('temperature')
            weight = serializer.validated_data.get('weight')
            diagnosis = serializer.validated_data.get('diagnosis')
            treatment = serializer.validated_data.get('treatment')
            
            is_deworm = serializer.validated_data.get('isDeworming')
            is_vaccine = serializer.validated_data.get('isVaccination')
            products_selected = serializer.validated_data.get('productsSelected')

            if appointment_date:
                if appointment_date < date.today():
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': 'Selected date is in the past.'})

                doctor_schedule_for_date = DoctorSchedule.objects.filter(date=appointment_date).first()

                if doctor_schedule_for_date and doctor_schedule_for_date.timeOfTheDay == "whole_day":
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': 'Doctor is not available the whole day on the selected date.'})
                
                if doctor_schedule_for_date and doctor_schedule_for_date.timeOfTheDay == appointment_time_of_the_day:
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': f'Doctor is not available in the {appointment_time_of_the_day} on the selected date.'})

                appointments_for_date = Appointment.objects.filter(date=appointment_date, isActive=True, status='pending').count()
                date_slot = DateSlot.objects.filter(date=appointment_date).first()
                max_appointment = MaximumAppointment.objects.first().max_appointments

                if date_slot:
                    max_allowed = date_slot.slots
                else:
                    max_allowed = max_appointment
                if appointments_for_date >= max_allowed:
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': 'No available slots on the selected date.'})

            try:
                with transaction.atomic():
                    
                    selected_pet = Pet.objects.get(pk=selected_pet_id)

                    appointment = None

                    if appointment_date:
                        selected_purpose = Service.objects.get(pk=appointment_purpose)

                        appointment = Appointment.objects.create(
                            pet=selected_pet,
                            client=selected_pet.client,
                            date=appointment_date,
                            timeOfTheDay=appointment_time_of_the_day,
                            purpose=selected_purpose,
                            status='pending',
                            isActive=True
                        )

                    pet_treatment = PetTreatment.objects.create(
                        pet_id=selected_pet.id,
                        treatment_date=datetime.now(),
                        symptoms=symptoms,
                        treatment_weight=weight,
                        temperature=temperature,
                        diagnosis=diagnosis,
                        treatment=treatment,
                        appointment=appointment if appointment else None,
                        isDeworm=is_deworm,
                        isVaccine=is_vaccine,
                        isActive=True
                    )

                    lab_results_descriptions = serializer.validated_data.get('labResultsDescriptions')
                    lab_results_image_ids = serializer.validated_data.get('labResultsImageIDS', [])

                    for index, description in enumerate(lab_results_descriptions):
                        lab_result_data = {
                            'description': description,
                            'image': lab_results_image_ids[index] if index < len(lab_results_image_ids) else None
                        }

                        if lab_result_data['image']:
                            temp_image = TemporaryLabResultImage.objects.get(id=lab_result_data['image'])
                            lab_result = LabResult.objects.create(
                                result_name=lab_result_data['description'],
                                result_image=temp_image.image
                            )
                            temp_image.delete()
                        else:
                            lab_result = LabResult.objects.create(
                                result_name=lab_result_data['description']
                            )
                        
                        pet_treatment.lab_results.add(lab_result)

                    if weight:
                        selected_pet.weight = weight
                        selected_pet.save()

                    if products_selected:
                        pet_medical_prescription = PetMedicalPrescription.objects.create(
                            pet_id=selected_pet.id,
                            date_prescribed=datetime.now(),
                            pet_treatment=pet_treatment,
                            isActive=True
                        )

                        medicines_for_session = []

                        for product_id, product_details in products_selected:
                            PrescriptionMedicines.objects.create(
                                prescription=pet_medical_prescription,
                                medicine_id=product_id,
                                strength=product_details['strength'],
                                #form=product_details['form'],
                                quantity=product_details['quantity'],
                                dosage=product_details['dosage'],
                                frequency=product_details['frequency'],
                                remarks=product_details['remarks']
                            )

                            medicines_for_session.append({
                                'id': product_id,
                                'details': product_details
                            })
                        

                        request.session['selected_medicines'] = medicines_for_session
                    
                    checkup_service = Service.objects.get(service_type="Doctor's Fee") #MAKE THIS DYNAMIC AT POLISHING
                    request.session['selected_service'] = checkup_service.id

                    pet_owner_id = selected_pet.client.user.id

                    return Response({'success': True, 'message': 'Consultation submitted successfully.', 'pet_owner_id': pet_owner_id})
            except Exception as e:
                return Response({'success': False, 'message': str(e)})
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@staff_required
@login_required
def view_prescription(request, prescription_id):
    prescription = get_object_or_404(PetMedicalPrescription, id=prescription_id)
    
    pet = prescription.pet
    client = pet.client

    prescription_medicines = PrescriptionMedicines.objects.filter(prescription=prescription)

    context = {
        'prescription': prescription,
        'pet': pet,
        'client': client,
        'prescription_medicines': prescription_medicines
    }
    
    return render(request, 'admin/prescription_module/view_prescription.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class LabResultImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        
        serializer = TemporaryLabResultImageSerializer(data=request.data)

        if serializer.is_valid():

            image = serializer.validated_data.get('image')

            if image:
                image_type = imghdr.what(image)
                if image_type not in ["jpeg", "png", "jpg", "webp"]:
                    return Response({'message': 'Invalid file type. Only .jpg, .jpeg, .png, and .webp files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({"message": "Image uploaded successfully!", "temp_image_id": serializer.instance.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@staff_required
@login_required
def add_medical_prescription(request):
    pets = Pet.objects.filter(is_active=True).order_by('-id')
    types = ProductType.objects.filter(name="Medicines")

    product_dict = {}
    for t in types:
        products = Product.objects.filter(type=t, active=True)
        filtered_products = [product for product in products if not product.is_product_expired() and not product.is_product_out_of_stock()]
        product_dict[t.name] = filtered_products

    formList = PrescriptionMedicines.MEDICINES_FORM_LIST

    context = {'pets': pets, 'product_dict': product_dict, 'formList': formList}
    return render(request, 'admin/prescription_module/prescription_module.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class SubmitPrescription(APIView):
    def post(self, request, *args, **kwargs):
        
        serializer = PrescriptionSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    selected_pet_id = serializer.validated_data.get('selectedPetId')
                    products_selected = serializer.validated_data.get('productsSelected')

                    selected_pet = Pet.objects.get(pk=selected_pet_id)
                    pet_owner_id = selected_pet.client.user.id

                    if products_selected:
                        pet_medical_prescription = PetMedicalPrescription.objects.create(
                            pet_id=selected_pet.id,
                            date_prescribed=datetime.now(),
                            isActive=True
                        )

                        medicines_for_session = []

                        for product_id, product_details in products_selected:
                            PrescriptionMedicines.objects.create(
                                prescription=pet_medical_prescription,
                                medicine_id=product_id,
                                strength=product_details['strength'],
                                #form=product_details['form'],
                                quantity=product_details['quantity'],
                                dosage=product_details['dosage'],
                                frequency=product_details['frequency'],
                                remarks=product_details['remarks']
                            )

                            medicines_for_session.append({
                                'id': product_id,
                                'details': product_details
                            })

                        checkup_service = Service.objects.get(service_type="Doctor's Fee")

                        request.session['selected_medicines'] = medicines_for_session
                        request.session['selected_service'] = checkup_service.id
                        
                        return Response({'success': True, "message": "Prescription has been added.", 'prescription_id': pet_medical_prescription.id, 'pet_owner_id': pet_owner_id}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'success': False, 'message': 'Please select at least one medicine.'})
            except Exception as e:
                return Response({'success': False, 'message': str(e)})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@staff_required
@login_required
def add_health_card_treatment(request):
    pets = Pet.objects.filter(is_active=True).order_by('-id')
    types = ProductType.objects.filter(name="Medicines")

    product_dict = {}
    for t in types:
        products = Product.objects.filter(type=t, active=True)
        filtered_products = [product for product in products if not product.is_product_expired() and not product.is_product_out_of_stock()]
        product_dict[t.name] = filtered_products

    formList = PrescriptionMedicines.MEDICINES_FORM_LIST

    services = Service.objects.filter(active=True)

    all_appointments = Appointment.objects.filter(isActive=True, status='pending').order_by('-id')
    max_appointment = MaximumAppointment.objects.first()
    date_slots = DateSlot.objects.all()
    doctor_schedules = DoctorSchedule.objects.all()

    all_appointments = serialize('json', all_appointments)
    date_slots = serialize('json', date_slots)
    doctor_schedules = serialize('json', doctor_schedules)

    context = {
        'pets': pets, 
        'product_dict': product_dict, 
        'formList': formList,
        'services': services ,
        'all_appointments': all_appointments,
        'max_appointment': max_appointment,
        'date_slots': date_slots,
        'doctor_schedules': doctor_schedules
    }
    return render(request, 'admin/health_card_module/health_card_module.html', context)

def get_scheduled_appointments_count(date):
    return Appointment.objects.filter(date=date, isActive=True).count()

def get_available_slots(date):
    date_slot = DateSlot.objects.filter(date=date, isActive=True).first()
    if date_slot:
        return date_slot.slots
    else:
        max_appointment = MaximumAppointment.objects.first()
        return max_appointment.max_appointments if max_appointment else 8

def check_doctor_schedule(date):
    schedule = DoctorSchedule.objects.filter(date=date, isActive=True).first()
    
    if not schedule:
        return 'morning'
    
    if schedule.timeOfTheDay == 'whole_day':
        return None
    elif schedule.timeOfTheDay == 'afternoon':
        return 'morning'
    elif schedule.timeOfTheDay == 'morning':
        return 'afternoon'
        
def create_appointment(pet, service, default_date, delta):
    appointment_date = default_date

    while True:
        if appointment_date.weekday() == 6:
            appointment_date += timedelta(days=1)
            continue 

        available_slots = get_available_slots(appointment_date)
        scheduled_appointments = get_scheduled_appointments_count(appointment_date)
        remaining_slots = available_slots - scheduled_appointments
        time_of_the_day = check_doctor_schedule(appointment_date)

        if remaining_slots > 0 and time_of_the_day:
            appointment = Appointment.objects.create(
                pet=pet,
                client=pet.client,
                date=appointment_date,
                timeOfTheDay=time_of_the_day,
                purpose=service,
                status='pending',
                isActive=True
            )
            break
        else:
            appointment_date += timedelta(days=1)

    return default_date + delta, appointment

@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class SubmitHealthCardTreatment(APIView):

    def post(self, request, *args, **kwargs):
        serializer = HealthCardSerializer(data=request.data)
        
        if(serializer.is_valid()):
            try:
                with transaction.atomic():
                    selected_pet_id = serializer.validated_data.get('selectedPetId')
                    selected_product_id = serializer.validated_data.get('productSelected')
                    medicine_sticker = serializer.validated_data.get('medicine_sticker')

                    temperature = serializer.validated_data.get('temperature')
                    weight = serializer.validated_data.get('weight')
                    treatment = serializer.validated_data.get('treatment')
                    isDeworm = serializer.validated_data.get('isDeworming')
                    isVaccine = serializer.validated_data.get('isVaccination')

                    appointment_cycle = serializer.validated_data.get('appointment_cycle')
                    appointment_cycle_repeat = serializer.validated_data.get('appointment_cycle_repeat')
                    appointment_cycle_repeat = 0 if not appointment_cycle_repeat else appointment_cycle_repeat
                    appointment_date = serializer.validated_data.get('appointment_date')
                    appointment_time_of_the_day = serializer.validated_data.get('appointment_time_of_the_day')
                    appointment_purpose = serializer.validated_data.get('appointment_purpose')

                    pet = Pet.objects.get(pk=selected_pet_id)

                    service = Service.objects.get(pk=appointment_purpose)

                    last_treatment = PetTreatment.objects.filter(
                        Q(pet_id=selected_pet_id) & 
                        Q(treatment=service.service_type) & 
                        (Q(isDeworm=True) | Q(isVaccine=True))
                    ).last()

                    previous_treatments = PetTreatment.objects.filter(
                        Q(pet_id=selected_pet_id) & 
                        Q(treatment=treatment) & 
                        (Q(isDeworm=True) | Q(isVaccine=True))
                    )

                    try:
                        all_done = all(cycle['status'] == 'done' for cycle in last_treatment.appointment_cycles)
                    except:
                        all_done = True

                    if previous_treatments.exists():
                        last_cycle_remaining = previous_treatments.last().cycles_remaining
                        if last_cycle_remaining > 0:  
                            last_cycle_remaining -= 1

                    if appointment_cycle:
                        if last_treatment and last_treatment.hasMultipleCycles:
                            last_treatment_cycle = last_treatment.cycles.all().order_by('-cycle_number').first()

                            if last_treatment_cycle and datetime.today().date() <= last_treatment_cycle.appointment.date:
                                return Response({'success': False, 'message': 'The previous treatment cycle for this pet is still active. You cannot start a new one.'})

                    if last_treatment:
                        last_treatment_appointment = last_treatment.appointment
                        if last_treatment_appointment:
                            last_treatment_appointment.isActive = False
                            last_treatment_appointment.status = 'done'
                            last_treatment_appointment.save()

                    if weight:
                        pet.weight = weight
                        pet.save()

                    if isDeworm:
                        lab_result_desc = "Deworming"
                    elif isVaccine:
                        lab_result_desc = "Vaccination"
                    else:
                        lab_result_desc = "medicine_sticker"

                    lab_result = LabResult.objects.create(
                        result_name=lab_result_desc,
                        result_image=medicine_sticker
                    )

                    if appointment_cycle and appointment_date:
                        return Response({'success': False, 'message': 'You can only select either appointment cycle or appointment date.'})

                    appointment = None

                    pet_treatment = PetTreatment(
                        pet_id=pet.id,
                        treatment_date=datetime.now(),
                        treatment_weight=weight,
                        temperature=temperature,
                        treatment=treatment,
                        isDeworm=isDeworm,
                        isVaccine=isVaccine,
                        cycles_remaining=last_cycle_remaining if previous_treatments.exists() else appointment_cycle_repeat
                    )

                    pet_treatment.save()

                    if not all_done:
                        for cycle in last_treatment.appointment_cycles:
                            if datetime.strptime(cycle['date'], "%Y-%m-%d").date() < datetime.today().date():
                                cycle['status'] = 'done'

                        future_appointments = [x for x in last_treatment.appointment_cycles if x['status'] == 'pending']

                        if future_appointments:
                            future_appointments[0]['status'] = 'done'
                            
                            if len(future_appointments) > 1:
                                next_appointment = future_appointments[1] 
                                next_appointment_id = next_appointment['appointment_id']

                                appointment = Appointment.objects.get(id=next_appointment_id)

                                pet_treatment.appointment = appointment

                            pet_treatment.appointment_cycles = last_treatment.appointment_cycles
                            pet_treatment.hasMultipleCycles = True
                            pet_treatment.save()
                    else:
                        if appointment_cycle:
                            if not appointment_cycle_repeat:
                                return Response({'success': False, 'message': 'Please enter the number of times the appointment cycle will repeat.'})

                            if appointment_cycle == "weekly":
                                delta = relativedelta(weeks=1)
                            elif appointment_cycle == "every-2-weeks":
                                delta = relativedelta(weeks=2)
                            elif appointment_cycle == "every-3-weeks":
                                delta = relativedelta(weeks=3)
                            elif appointment_cycle == "monthly":
                                delta = relativedelta(months=1)
                            elif appointment_cycle == "quarterly":
                                delta = relativedelta(months=3)
                            elif appointment_cycle == "semi-annually":
                                delta = relativedelta(months=6)
                            elif appointment_cycle == "annually":
                                delta = relativedelta(years=1)
                            else:
                                delta = None

                            if not appointment_date and delta:
                                appointment_date = datetime.today().date() + delta

                            appointments = []

                            for i in range(appointment_cycle_repeat):
                                
                                next_appointment_date, new_appointment = create_appointment(pet, service, appointment_date, delta)

                                appointments.append({
                                    'date': new_appointment.date.strftime("%Y-%m-%d"),
                                    'appointment_id': new_appointment.id,
                                    'status': 'pending'
                                })
                                appointment_date += delta

                            first_appointment_id = appointments[0]['appointment_id']
                            appointment = Appointment.objects.get(id=first_appointment_id)

                            pet_treatment.appointment_cycles = appointments
                            pet_treatment.hasMultipleCycles = True
                            pet_treatment.save()
                        elif appointment_date:
                            appointment = Appointment.objects.create(
                                pet=pet,
                                client=pet.client,
                                date=appointment_date,
                                timeOfTheDay=appointment_time_of_the_day,
                                purpose=service if appointment_purpose else custom_purpose,
                                status='pending',
                                isActive=True
                            )

                    pet_treatment.appointment = appointment  
                    pet_treatment.save()

                    pet_treatment.lab_results.add(lab_result)

                    pet_medical_prescription = PetMedicalPrescription.objects.create(
                        pet_id=pet.id,
                        date_prescribed=datetime.now(),
                        pet_treatment=pet_treatment,
                        isActive=True
                    )

                    medicines_for_session = []

                    PrescriptionMedicines.objects.create(
                        prescription=pet_medical_prescription,
                        medicine_id=selected_product_id,
                        #form=product_details['form'],
                        quantity=1,
                    )

                    medicines_for_session.append({
                        'id': selected_product_id,
                        'details': {
                            'strength': '',
                            'quantity': 1,
                            'dosage': '',
                            'frequency': '',
                            'remarks': ''
                        }
                    })

                    if isDeworm:
                        checkup_service = Service.objects.get(service_type="Deworming")
                    elif isVaccine:
                        checkup_service = Service.objects.get(service_type="Vaccination")
                    else:
                        checkup_service = Service.objects.get(service_type="Doctor's Fee")

                    request.session['selected_medicines'] = medicines_for_session
                    request.session['selected_service'] = checkup_service.id

                    pet_owner_id = pet.client.user.id

                    return Response({'success': True, 'message': 'Health card treatment submitted successfully.', 'pet_owner_id': pet_owner_id})
            except Exception as e:
                return Response({'success': False, 'message': str(e)})
        else:
            return Response({'success': False, 'message': serializer.errors})

@login_required
@staff_required
def get_treatment_cycle_status(request, petID):
    try:
        treatmentType = request.GET.get('treatmentType', None)
        treatmentType = treatmentType[0].upper() + treatmentType[1:]
        treatments = PetTreatment.objects.filter(pet_id=petID, treatment=treatmentType).order_by('-id')

        for treatment in treatments:
            appointment_cycles = treatment.appointment_cycles
            if appointment_cycles:
                # Filter cycles which are 'done'
                done_cycles = [cycle for cycle in appointment_cycles if cycle['status'] == 'done']

                # Check if all corresponding Appointments for these cycles are inactive
                all_inactive = all(
                    not Appointment.objects.filter(id=cycle['appointment_id'], isActive=True).exists() 
                    for cycle in done_cycles
                )

                cycle_status = len(done_cycles) == len(appointment_cycles) and all_inactive

                if cycle_status:
                    return JsonResponse({'success': True, 'appointment_cycles': appointment_cycles, 'cycle_status': cycle_status})
                else:
                    return JsonResponse({'success': True, 'appointment_cycles': appointment_cycles, 'cycle_status': cycle_status})

        return JsonResponse({'success': False, 'message': 'No pet treatment with relevant cycles found.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})





@staff_required
@login_required
def get_laboratory_results_data(request, treatmentID):

    if request.method == 'GET':
        pet_treatment = PetTreatment.objects.get(pk=treatmentID)

        lab_results = pet_treatment.lab_results.all()

        lab_results_data = []

        for lab_result in lab_results:
            lab_results_data.append({
                'id': lab_result.id,
                'name': lab_result.result_name,
                'image': lab_result.result_image.url if lab_result.result_image else None
            })
        
        return JsonResponse({'success': True, 'lab_results_data': lab_results_data})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

@staff_required
@login_required
def update_medical_record(request, treatmentID):
    pets = Pet.objects.filter(is_active=True).order_by('-id')
    types = ProductType.objects.filter(name="Medicines")

    product_dict = {}
    for t in types:
        products = Product.objects.filter(type=t, active=True)
        filtered_products = [product for product in products if not product.is_product_expired() and not product.is_product_out_of_stock()]
        product_dict[t.name] = filtered_products

    formList = PrescriptionMedicines.MEDICINES_FORM_LIST

    services = Service.objects.filter(active=True)

    all_appointments = Appointment.objects.filter(isActive=True, status='pending').order_by('-id')
    max_appointment = MaximumAppointment.objects.first()
    date_slots = DateSlot.objects.all()
    doctor_schedules = DoctorSchedule.objects.all()

    all_appointments = serialize('json', all_appointments)
    date_slots = serialize('json', date_slots)
    doctor_schedules = serialize('json', doctor_schedules)

    pet_treatment = PetTreatment.objects.get(pk=treatmentID)

    laboratory_results = pet_treatment.lab_results.all()
    
    one_laboratory_results = None

    if len(laboratory_results) == 1:
        one_laboratory_results = laboratory_results.first()

    prescription_medicines = PrescriptionMedicines.objects.filter(prescription__pet_treatment=pet_treatment)

    product_ids = set(prescription_medicines.values_list('medicine_id', flat=True))

    products_map = {}

    for product in prescription_medicines.values('medicine_id', 'medicine__product_name', 'strength', 'quantity', 'dosage', 'frequency', 'remarks'):
        
        product_id = product['medicine_id']
        product_details = {
            'product_name': product['medicine__product_name'],  # Fetching product_name
            'strength': product['strength'],
            'quantity': product['quantity'],
            'dosage': product['dosage'],
            'frequency': product['frequency'],
            'remarks': product['remarks'],
        }
        products_map[product_id] = product_details

    appointment = pet_treatment.appointment
    
    context = {
        'pets': pets, 
        'product_dict': product_dict, 
        'formList': formList,
        'services': services ,
        'all_appointments': all_appointments,
        'max_appointment': max_appointment,
        'date_slots': date_slots,
        'doctor_schedules': doctor_schedules,
        'treatmentID': treatmentID,
        'pet_treatment': pet_treatment,
        'laboratory_results': laboratory_results,
        'one_laboratory_results': one_laboratory_results,
        'prescription_medicines': prescription_medicines,
        'product_ids': product_ids,
        'products_map': products_map,
        'appointment': appointment
    }
    return render(request, 'admin/consultation_module/update/update.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(staff_required, name='dispatch')
class UpdateConsultationView(APIView):

    throttle_scope = 'submit_consultation'

    def post(self, request, *args, **kwargs):
        serializer = UpdateConsultationSerializer(data=request.data)
        #print(serializer)

        if serializer.is_valid():
            treatment_id = serializer.validated_data.get('treatmentId')
            selected_pet_id = serializer.validated_data.get('selectedPetId')
            appointment_date = serializer.validated_data.get('appointment_date')
            appointment_time_of_the_day = serializer.validated_data.get('appointment_time_of_the_day')
            appointment_purpose = serializer.validated_data.get('appointment_purpose')
            symptoms = serializer.validated_data.get('symptoms')
            temperature = serializer.validated_data.get('temperature')
            weight = serializer.validated_data.get('weight')
            diagnosis = serializer.validated_data.get('diagnosis')
            treatment = serializer.validated_data.get('treatment')
            
            is_deworm = serializer.validated_data.get('isDeworming')
            is_vaccine = serializer.validated_data.get('isVaccination')
            products_selected = serializer.validated_data.get('productsSelected')

            if appointment_date:
                if appointment_date < date.today():
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': 'Selected date is in the past.'})

                doctor_schedule_for_date = DoctorSchedule.objects.filter(date=appointment_date).first()

                if doctor_schedule_for_date and doctor_schedule_for_date.timeOfTheDay == "whole_day":
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': 'Doctor is not available the whole day on the selected date.'})
                
                if doctor_schedule_for_date and doctor_schedule_for_date.timeOfTheDay == appointment_time_of_the_day:
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': f'Doctor is not available in the {appointment_time_of_the_day} on the selected date.'})

                appointments_for_date = Appointment.objects.filter(date=appointment_date, isActive=True, status='pending').count()
                date_slot = DateSlot.objects.filter(date=appointment_date).first()
                max_appointment = MaximumAppointment.objects.first().max_appointments

                if date_slot:
                    max_allowed = date_slot.slots
                else:
                    max_allowed = max_appointment
                if appointments_for_date >= max_allowed:
                    return JsonResponse({'success': False, 'appointment_error': True, 'message': 'No available slots on the selected date.'})

            try:
                with transaction.atomic():
                    
                    selected_pet = Pet.objects.get(pk=selected_pet_id)

                    pet_treatment, created = PetTreatment.objects.get_or_create(
                        id=treatment_id,
                        defaults={
                            'pet_id': selected_pet.id,
                            'treatment_date': datetime.now(),
                            'symptoms': symptoms,
                            'treatment_weight': weight,
                            'temperature': temperature,
                            'diagnosis': diagnosis,
                            'treatment': treatment,
                            'isDeworm': is_deworm,
                            'isVaccine': is_vaccine,
                            'isActive': True
                        }
                    )

                    if not created:
                        pet_treatment.symptoms = symptoms
                        pet_treatment.treatment_weight = weight
                        pet_treatment.temperature = temperature
                        pet_treatment.diagnosis = diagnosis
                        pet_treatment.treatment = treatment
                        pet_treatment.isDeworm = is_deworm
                        pet_treatment.isVaccine = is_vaccine
                        pet_treatment.save()

                    if appointment_date:
                        selected_purpose = Service.objects.get(pk=appointment_purpose)

                        # If the treatment already has an appointment, update it, else create a new one
                        if pet_treatment.appointment:
                            appointment = pet_treatment.appointment
                            appointment.pet = selected_pet
                            appointment.client = selected_pet.client
                            appointment.date = appointment_date
                            appointment.timeOfTheDay = appointment_time_of_the_day
                            appointment.purpose = selected_purpose
                            appointment.status = 'pending'
                            appointment.isActive = True
                            appointment.save()
                        else:
                            appointment = Appointment.objects.create(
                                pet=selected_pet,
                                client=selected_pet.client,
                                date=appointment_date,
                                timeOfTheDay=appointment_time_of_the_day,
                                purpose=selected_purpose,
                                status='pending',
                                isActive=True
                            )
                            pet_treatment.appointment = appointment
                            pet_treatment.save()

                    # lab_results_descriptions = serializer.validated_data.get('labResultsDescriptions', [])

                    # lab_results_image_ids = serializer.validated_data.get('labResultsImageIDS', [])

                    labResults = serializer.validated_data.get('labResults')

                    existing_lab_results = set(pet_treatment.lab_results.values_list('id', flat=True))

                    processed_lab_results = set()

                    for lab_result_item in labResults:
                        description = lab_result_item['description']
                        image_id = lab_result_item['image_id']
                        lab_result_id = lab_result_item['lab_result_id']

                        defaults = {'result_name': description}

                        if image_id:
                            temp_image = TemporaryLabResultImage.objects.get(id=image_id)
                            defaults['result_image'] = temp_image.image
                        else:
                            if not lab_result_id or (lab_result_id and int(lab_result_id) not in existing_lab_results):
                                try:
                                    existing_lab_result = LabResult.objects.filter(id__in=existing_lab_results).first()
                                    if existing_lab_result:
                                        defaults['result_image'] = existing_lab_result.result_image
                                except LabResult.DoesNotExist:
                                    pass

                        if lab_result_id:
                            lab_result, created = LabResult.objects.update_or_create(
                                id=lab_result_id,
                                defaults=defaults
                            )
                        else:
                            lab_result = LabResult.objects.create(**defaults)

                        if image_id:
                            temp_image.delete()

                        processed_lab_results.add(lab_result.id)
                        pet_treatment.lab_results.add(lab_result)

                    lab_results_to_remove = existing_lab_results - processed_lab_results
                    for lab_result_id in lab_results_to_remove:
                        lab_result = LabResult.objects.get(id=lab_result_id)
                        pet_treatment.lab_results.remove(lab_result)
                        lab_result.isActive = False
                        lab_result.save()

                    if weight:
                        selected_pet.weight = weight
                        selected_pet.save()

                    if products_selected:
                        pet_medical_prescription, created = PetMedicalPrescription.objects.get_or_create(
                            pet_id=selected_pet.id,
                            pet_treatment=pet_treatment,
                            defaults={
                                'date_prescribed': datetime.now(),
                                'isActive': True
                            }
                        )

                        current_medicines = set(PrescriptionMedicines.objects.filter(prescription=pet_medical_prescription).values_list('medicine_id', flat=True))
                        new_medicines = set(int(product_id) for product_id, product_details in products_selected)

                        medicines_to_delete = current_medicines - new_medicines
                        PrescriptionMedicines.objects.filter(prescription=pet_medical_prescription, medicine_id__in=medicines_to_delete).delete()

                        medicines_for_session = []

                        for product_id, product_details in products_selected:
                            PrescriptionMedicines.objects.update_or_create(
                                prescription=pet_medical_prescription,
                                medicine_id=product_id,
                                defaults={
                                    'strength': product_details['strength'],
                                    # 'form': product_details['form'], # Removed as it's deprecated
                                    'quantity': product_details['quantity'],
                                    'dosage': product_details['dosage'],
                                    'frequency': product_details['frequency'],
                                    'remarks': product_details['remarks']
                                }
                            )

                            medicines_for_session.append({
                                'id': product_id,
                                'details': product_details
                            })

                        request.session['selected_medicines'] = medicines_for_session

                    
                    checkup_service = Service.objects.get(service_type="Doctor's Fee") #MAKE THIS DYNAMIC AT POLISHING
                    request.session['selected_service'] = checkup_service.id

                    pet_owner_id = selected_pet.client.user.id

                    return Response({'success': True, 'message': 'Consultation updated successfully.', 'pet_owner_id': pet_owner_id})
            except Exception as e:
                return Response({'success': False, 'message': str(e)})
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@staff_required
@login_required
def delete_treatment(request, treatmentID):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                pet_treatment = PetTreatment.objects.get(pk=treatmentID)
                pet_treatment.isActive = False
                pet_treatment.save()
                return JsonResponse({'success': True, 'message': 'Treatment deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

@staff_required
@login_required
def enable_treatment(request, treatmentID):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                pet_treatment = PetTreatment.objects.get(pk=treatmentID)
                pet_treatment.isActive = True
                pet_treatment.save()
                return JsonResponse({'success': True, 'message': 'Treatment enabled successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

@staff_required
@login_required
def update_health_card_record(request, treatmentID):
    types = ProductType.objects.filter(name="Medicines")

    product_dict = {}
    for t in types:
        products = Product.objects.filter(type=t, active=True)
        filtered_products = [product for product in products if not product.is_product_expired() and not product.is_product_out_of_stock()]
        product_dict[t.name] = filtered_products

    formList = PrescriptionMedicines.MEDICINES_FORM_LIST

    services = Service.objects.filter(active=True)

    all_appointments = Appointment.objects.filter(isActive=True, status='pending').order_by('-id')
    max_appointment = MaximumAppointment.objects.first()
    date_slots = DateSlot.objects.all()
    doctor_schedules = DoctorSchedule.objects.all()

    all_appointments = serialize('json', all_appointments)
    date_slots = serialize('json', date_slots)
    doctor_schedules = serialize('json', doctor_schedules)

    pet_treatment = PetTreatment.objects.get(pk=treatmentID)

    try:
        medical_prescription = PetMedicalPrescription.objects.get(pet_treatment=pet_treatment)
        prescription_medicines = PrescriptionMedicines.objects.filter(prescription=medical_prescription).first()
    except PetMedicalPrescription.DoesNotExist:
        medical_prescription = None
        prescription_medicines = None

    lab_results = PetTreatment.objects.get(pk=treatmentID).lab_results.first()
    appointment = pet_treatment.appointment

    context = {
        'product_dict': product_dict, 
        'formList': formList,
        'services': services ,
        'all_appointments': all_appointments,
        'max_appointment': max_appointment,
        'date_slots': date_slots,
        'doctor_schedules': doctor_schedules,
        'treatmentID': treatmentID,
        'pet_treatment': pet_treatment,
        'medical_prescription': medical_prescription,
        'prescription_medicines': prescription_medicines,
        'lab_results': lab_results,
        'appointment': appointment
    }

    return render(request, 'admin/health_card_module/update/index_update.html', context)

@staff_required
@login_required
def submit_update_health_card(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                
                treatmentID = request.POST.get('treatmentID')

                product_selected = request.POST.get('productSelected')
                pet_id = request.POST.get('petID')
                appointment_date = request.POST.get('appointment_date')
                appointment_date = datetime.strptime(appointment_date, '%b %d, %Y').strftime('%Y-%m-%d')
                appointment_time_of_the_day = request.POST.get('appointment_time_of_the_day')
                appointment_purpose = request.POST.get('appointment_purpose')
                temperature = request.POST.get('temperature')
                weight = request.POST.get('weight')
                treatment = request.POST.get('treatment')
                isDeworm = request.POST.get('isDeworming')
                isVaccine = request.POST.get('isVaccination')
                medicine_sticker = request.FILES.get('medicine_sticker')

                pet_treatment = PetTreatment.objects.get(pk=treatmentID)
                appointment = pet_treatment.appointment
                
                if isDeworm == 'true':
                    pet_treatment.isVaccine = False
                    pet_treatment.isDeworm = True
                    pet_treatment.save()
                    lab_result_desc = "Deworming"
                elif isVaccine == 'true':
                    pet_treatment.isDeworm = False
                    pet_treatment.isVaccine = True
                    pet_treatment.save()
                    lab_result_desc = "Vaccination"
                else:
                    lab_result_desc = "medicine_sticker"
                print(pet_treatment.isDeworm)
                print(pet_treatment.isVaccine)
                if appointment:
                    if appointment_date:
                        appointment.date = appointment_date
                        appointment.timeOfTheDay = appointment_time_of_the_day
                        appointment.purpose_id = appointment_purpose
                        appointment.save()

                try:
                    medical_prescription = PetMedicalPrescription.objects.get(pet_treatment=pet_treatment)
                    prescription_medicines = PrescriptionMedicines.objects.filter(prescription=medical_prescription).first()
                except PetMedicalPrescription.DoesNotExist:
                    medical_prescription = None
                    prescription_medicines = None
                
                pet = pet_treatment.pet

                if not medical_prescription:
                    pet_medical_prescription = PetMedicalPrescription.objects.create(
                        pet=pet,
                        date_prescribed=datetime.now(),
                        pet_treatment=pet_treatment,
                        isActive=True
                    )

                    product = Product.objects.get(pk=product_selected)

                    PrescriptionMedicines.objects.create(
                        prescription=pet_medical_prescription,
                        medicine=product,
                        #form=product_details['form'],
                        quantity=1,
                    )
                else:
                    prescription_medicines.medicine_id = product_selected
                    prescription_medicines.save()

                laboratory_result = pet_treatment.lab_results.first()
                
                if not laboratory_result:
                    lab_result = LabResult.objects.create(
                        result_name=lab_result_desc,
                        result_image=medicine_sticker
                    )
                    pet_treatment.lab_results.add(lab_result)
                else:
                    laboratory_result.result_name = lab_result_desc
                    if medicine_sticker:
                        laboratory_result.result_image = medicine_sticker
                    laboratory_result.save()
                
                if treatment != 'undefined':
                    pet_treatment.treatment = treatment
                    pet_treatment.save()

                pet_treatment.temperature = temperature
                pet_treatment.treatment_weight = weight
                pet_treatment.save()

                pet.weight = weight
                pet.save()
                
                return JsonResponse({'success': True, 'message': 'Treatment updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})