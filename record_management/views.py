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
            if not hasattr(user, 'client'):
                login(request, user)
                return redirect('register-client-page')
            else:
                # Generate and send the OTP
                phone_number = user.client.contact_number
                otp_code = send_otp_sms(phone_number)

                # Store the OTP code and user ID in the session
                request.session['otp_code'] = otp_code
                request.session['temp_user_id'] = user.id

                # Save the session data explicitly
                request.session.save()

                # Redirect to the OTP verification page with the session ID
                return redirect('otp_view', sessionid=request.session.session_key)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@csrf_exempt
def otp_view(request, sessionid):
    if request.session.session_key != sessionid:
        return HttpResponse("Unauthorized access.", status=403)

    if request.method == 'POST':
        entered_otp_code = int(request.POST.get('otp_code'))
        stored_otp_code = int(request.session.get('otp_code', None))

        if entered_otp_code != stored_otp_code:
            # Return an error message if the OTP is not valid
            return render(request, 'otp.html', {'error_message': 'Invalid OTP. Please try again.'})

        if entered_otp_code == stored_otp_code:
            # Clear the OTP code from the session
            del request.session['otp_code']

            # Log in the user and redirect to the home page
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
            # Return an error message if the OTP is not valid
            # Delete the user and client
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

            # Generate and send the OTP
            phone_number = client.contact_number
            otp_code = send_otp_sms(phone_number)

            # Store the OTP code in the session
            request.session['otp_code'] = otp_code
            request.session['temp_user_id'] = user.id

            request.session.save()

            # Redirect to the OTP verification page
            return redirect('otp_view', sessionid=request.session.session_key)
    else:
        form = CombinedRegistrationForm()

    context = {'form': form}
    return render(request, 'client_register.html', context)

# def register_client(request):
#     if request.user.is_authenticated and hasattr(request.user, 'client'):
#         return redirect('home')

#     if request.method == 'POST':
#         form = ClientInfoForm(request.POST)
#         if form.is_valid():
#             user_id = request.session.get('temp_user_id')
#             if user_id:
#                 user = User.objects.get(id=user_id)
#             else:
#                 return HttpResponse("An error occurred. Please try again.")

#             client = Client(user=user,
#                             first_name=form.cleaned_data['first_name'],
#                             last_name=form.cleaned_data['last_name'],
#                             address=form.cleaned_data['address'],
#                             contact_number=form.cleaned_data['contact_number'])
#             client.save()

#             # Generate and send the OTP
#             phone_number = client.contact_number
#             otp_code = send_otp_sms(phone_number)

#             # Store the OTP code in the session
#             request.session['otp_code'] = otp_code

#             # Redirect to the OTP verification page
#             return redirect('otp_view')
#     else:
#         form = ClientInfoForm()

#     context = {'form': form}
#     return render(request, 'client_info.html', context)

# def register_user(request):
#     if request.user.is_authenticated:
#         return redirect('home')

#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  # Set is_active to False initially
#             user.save()

#             # Store the user ID in the session
#             request.session['temp_user_id'] = user.id
#             request.session.save()
#             return redirect('register-client-page')
#     else:
#         form = UserRegistrationForm()

#     context = {'form': form}
#     return render(request, 'client_register.html', context)

# @login_required
# def cancel_registration(request):
#     user = request.user
#     #logout(request)  # Log out the user
#     user.delete()  # Delete the user
#     return redirect('home')  # Replace 'home' with the name of the URL pattern for the home page

# @login_required
# def registration_success(request):
#     return render(request, 'client_success.html')

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
