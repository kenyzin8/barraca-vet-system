from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages

from .forms import ClientInfoForm, UserRegistrationForm, PetRegistrationForm, LoginForm
from .models import Client, Pet

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # return redirect('register-pet-page')
            return redirect('home')
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
            user.is_active = True  # Set is_active to False initially
            user.save()
            login(request, user)  # Log in the user
            return redirect('register-client-page')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'client_register.html', context)

@login_required
def register_client(request):
    user = request.user
    if hasattr(user, 'client'):
        messages.error(request, 'You have already submitted your client information.')
        return redirect('home')  # Replace 'home' with the name of the URL pattern for the page you want to redirect to

    if request.method == 'POST':
        form = ClientInfoForm(request.POST)
        if form.is_valid():
            user.is_active = True
            user.save()
            client = Client(user=user,
                            first_name=form.cleaned_data['first_name'],
                            last_name=form.cleaned_data['last_name'],
                            address=form.cleaned_data['address'],
                            contact_number=form.cleaned_data['contact_number'])
            client.save()
            return redirect('client-success-page')  # Replace 'success' with the name of the URL pattern for the success page
    else:
        form = ClientInfoForm()

    context = {'form': form}
    return render(request, 'client_info.html', context)

@login_required
def cancel_registration(request):
    user = request.user
    logout(request)  # Log out the user
    user.delete()  # Delete the user
    return redirect('home')  # Replace 'home' with the name of the URL pattern for the home page

@login_required
def registration_success(request):
    return render(request, 'client_success.html')

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
    return render(request, 'pet_success.html')

@login_required
def view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    context = {'pet': pet}
    return render(request, 'view_pet.html', context)

@login_required
def update_pet(request, pet_id):
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
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        pet.delete()
        return redirect('pet-list-page')
    context = {'pet': pet}
    return render(request, 'delete_pet.html', context)

@login_required
def pet_list(request):
    pets = Pet.objects.filter(client=request.user.client)
    context = {'pets': pets}
    return render(request, 'pet_list.html', context)