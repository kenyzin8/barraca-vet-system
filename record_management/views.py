from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta

import json
import time

from .forms import PetRegistrationForm, LoginForm, UserRegistrationForm, UserUpdateForm, ClientUpdateForm, AdminPetRegistrationForm
from .models import Client, Pet
from django.contrib.auth import login, logout
from core.semaphore import send_sms, send_otp_sms
from core.decorators import staff_required
from django.core.cache import cache

from django.conf import settings

OTP_EXPIRATION_MINUTE = settings.OTP_EXPIRATION_MINUTES

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
        client_ip = get_client_ip(request)

        attempts_key = f'attempts_{client_ip}'
        attempts = cache.get(attempts_key, 0)

        if attempts >= 2:
            messages.error(request, 'Too many attempts. Please try again after 2 minutes.')
            return render(request, 'client/login.html', {'form': form})

        try:
            user = User.objects.get(username=username)
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
        except User.DoesNotExist:
            pass

        if form.is_valid():
            user = form.get_user()

            if not user.client.two_auth_enabled:
                login(request, user)
                cache.set(attempts_key, 0, 2 * 60) 
                return redirect('home')

            phone_number = user.client.contact_number
            otp_code = send_otp_sms(phone_number)

            request.session['otp_code'] = otp_code
            request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTE)).timestamp()
            request.session['temp_user_id'] = user.id
            request.session['temp_user_session'] = request.session.session_key
            request.session['otp_attempt_count'] = 0
            request.session.save()

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
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            client = Client(user=user,
                            first_name=form.cleaned_data['first_name'],
                            last_name=form.cleaned_data['last_name'],
                            address=form.cleaned_data['address'],
                            contact_number=form.cleaned_data['contact_number'])
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

@csrf_exempt
def otp_view(request):
    otp_expiration_timestamp = request.session.get('otp_code_expiration', 0)
    time_remaining = max(0, int(otp_expiration_timestamp - datetime.now().timestamp()))
    user_id = request.session.get('temp_user_id')
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

@csrf_exempt
def resend_otp(request):
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
        return HttpResponse("An error occurred. Please try again.")

@login_required
def register_pet(request):
    if request.method == 'POST':
        form = PetRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.client = request.user.client
            pet.save()
            return redirect('pet-list-page')
    else:
        form = PetRegistrationForm()

    context = {'form': form}
    return render(request, 'client/pet_register.html', context)

@login_required
def view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if pet.client != request.user.client:
        return redirect('pet-list-page')

    context = {'pet': pet}
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

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
    if pet.client != request.user.client:
        return redirect('pet-list-page')

    if request.method == 'POST':
        #set is_active to False
        pet.is_active = False
        pet.save()
        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})

@login_required
def pet_list(request):
    pets = Pet.objects.filter(client=request.user.client).order_by('-id')
    context = {'pets': pets}
    return render(request, 'client/pet_list.html', context)

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
    return render(request, 'admin/pet_module.html', context)

@staff_required
@login_required
def admin_view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    context = {'pet': pet}
    return render(request, 'admin/view_pet.html', context)

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
    return render(request, 'admin/update_pet.html', context)