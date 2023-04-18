from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

import json

from .forms import PetRegistrationForm, LoginForm, CombinedRegistrationForm
from .models import Client, Pet
from django.contrib.auth import login, logout
from core.sms import send_sms, send_otp_sms

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
            request.session['temp_user_id'] = user.id

            request.session.save()

            return redirect('otp_view', sessionid=request.session.session_key)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CombinedRegistrationForm(request.POST)
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
            request.session['temp_user_id'] = user.id

            request.session.save()

            return redirect('otp_view', sessionid=request.session.session_key)
    else:
        form = CombinedRegistrationForm()

    context = {'form': form}
    return render(request, 'client_register.html', context)

@csrf_exempt
def otp_view(request, sessionid):
    if request.session.session_key != sessionid:
        return HttpResponse("Unauthorized access.", status=403)

    if request.method == 'POST':
        entered_otp_code = int(request.POST.get('otp_code'))
        stored_otp_code = int(request.session.get('otp_code', None))

        if entered_otp_code != stored_otp_code:
            return render(request, 'otp.html', {'error_message': 'Invalid OTP. Please try again.'})

        if entered_otp_code == stored_otp_code:
            del request.session['otp_code']

            user_id = request.session.get('temp_user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                login(request, user)

                del request.session['temp_user_id']

                return redirect('home')
            else:
                return HttpResponse("An error occurred. Please try again.")
        else:
            user_id = request.session.get('temp_user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                user.delete()
            return HttpResponse("Invalid OTP. Please try again.")
    else:
        user_id = request.session.get('temp_user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            contact_number = user.client.contact_number
            return render(request, 'otp.html', {'contact_number': contact_number})
        else:
            return HttpResponse("An error occurred. Please try again.")

@login_required
def register_pet(request):
    if request.method == 'POST':
        form = PetRegistrationForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.client = request.user.client
            pet.save()
            return redirect('pet-success-page')
    else:
        form = PetRegistrationForm()

    context = {'form': form}
    return render(request, 'pet_register.html', context)

@login_required
def pet_registration_success(request):
    if request.user.is_authenticated and not hasattr(request.user, 'client'):
        return redirect('register-client-page')
    return render(request, 'pet_success.html')

@login_required
def view_pet(request, pet_id):
    if request.user.is_authenticated and not hasattr(request.user, 'client'):
        return redirect('register-client-page')
    pet = get_object_or_404(Pet, id=pet_id)
    context = {'pet': pet}
    return render(request, 'view_pet.html', context)

@login_required
def update_pet(request, pet_id):
    if request.user.is_authenticated and not hasattr(request.user, 'client'):
        return redirect('register-client-page')
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        form = PetRegistrationForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('view-pet-page', pet_id=pet.id)
    else:
        form = PetRegistrationForm(instance=pet)
    
    context = {'form': form, 'pet': pet}
    return render(request, 'update_pet.html', context)

@login_required
def delete_pet(request, pet_id):
    if request.user.is_authenticated and not hasattr(request.user, 'client'):
        return redirect('register-client-page')
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        pet.delete()
        return redirect('pet-list-page')
    context = {'pet': pet}
    return render(request, 'delete_pet.html', context)

@login_required
def pet_list(request):
    if request.user.is_authenticated and not hasattr(request.user, 'client'):
        return redirect('register-client-page')
    pets = Pet.objects.filter(client=request.user.client)
    context = {'pets': pets}
    return render(request, 'pet_list.html', context)
