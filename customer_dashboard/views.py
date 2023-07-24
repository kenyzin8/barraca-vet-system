from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from record_management.models import Pet
from appointment_management.models import Appointment

# Create your views here.
@login_required
def customer_dashboard(request):
    pets = Pet.objects.filter(client=request.user.client, is_active=True).order_by('-id')[:3]
    my_appointment = Appointment.objects.filter(client=request.user.client, isActive=True).order_by('date')

    pets_appointments = []
    for pet in pets:
        pet_appointment = {}
        pet_appointment['pet'] = pet
        pet_appointment['first_appointment'] = Appointment.objects.filter(pet=pet, isActive=True).order_by('date').first()
        pets_appointments.append(pet_appointment)

    context = {"pets": pets, "my_appointment": my_appointment, "pets_appointments": pets_appointments}
    return render(request, 'customer_dashboard.html', context)
