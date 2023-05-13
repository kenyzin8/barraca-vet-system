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

from .forms import PetRegistrationForm, LoginForm, UserRegistrationForm, UserUpdateForm, ClientUpdateForm
from .models import Client, Pet
from django.contrib.auth import login, logout
from core.semaphore import send_sms, send_otp_sms
from core.decorators import staff_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not user.client.two_auth_enabled:
                login(request, user)
                return redirect('home')
                
            phone_number = user.client.contact_number
            otp_code = send_otp_sms(phone_number)

            request.session['otp_code'] = otp_code
            request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=5)).timestamp()
            request.session['temp_user_id'] = user.id
            request.session['temp_user_session'] = request.session.session_key
            request.session.save()

            return redirect('otp_view')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

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
            request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=5)).timestamp()  # 5 minutes from now
            request.session['temp_user_id'] = user.id
            request.session['temp_user_session'] = request.session.session_key
            request.session.save()

            return redirect('otp_view')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'client_register.html', context)

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

    return render(request, 'client_account_settings.html', context)

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

    return render(request, 'admin_account_settings.html', context)

@csrf_exempt
def otp_view(request):
    otp_expiration_timestamp = request.session.get('otp_code_expiration', 0)
    time_remaining = max(0, int(otp_expiration_timestamp - datetime.now().timestamp()))
    user_id = request.session.get('temp_user_id')
    otp_expired = False
    if request.method == 'POST':
        entered_otp_code = int(request.POST.get('otp_code'))
        stored_otp_code = int(request.session.get('otp_code', None))

        if datetime.now().timestamp() > otp_expiration_timestamp:
            otp_expired = True
            return render(request, 'otp.html', {'error_message': 'Expired OTP. Please try again.', 'time_remaining': time_remaining, 'otp_expired': otp_expired})

        if entered_otp_code != stored_otp_code:
            return render(request, 'otp.html', {'error_message': 'Invalid OTP. Please try again.', 'time_remaining': time_remaining})

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
            return render(request, 'otp.html', {'contact_number': contact_number, 'time_remaining': time_remaining})
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

        request.session['otp_code'] = otp_code
        request.session['otp_code_expiration'] = (datetime.now() + timedelta(minutes=5)).timestamp()
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
    return render(request, 'pet_register.html', context)

@login_required
def view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if pet.client != request.user.client:
        return redirect('pet-list-page')

    context = {'pet': pet}
    return render(request, 'view_pet.html', context)

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
    return render(request, 'update_pet.html', context)

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
    if pet.client != request.user.client:
        return redirect('pet-list-page')

    if request.method == 'POST':
        pet.delete()
        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})

@login_required
def pet_list(request):
    pets = Pet.objects.filter(client=request.user.client).order_by('-id')
    context = {'pets': pets}
    return render(request, 'pet_list.html', context)
