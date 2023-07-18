from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Service
from django.http import JsonResponse
from .forms import ServiceForm
from django.db.models import Q
from copy import deepcopy

@staff_required
@login_required
def service_list(request):
    services = Service.objects.filter(active=True).order_by('-id')
    context = {'services': services}
    return render(request, 'services_list.html', context)

@staff_required
@login_required
def service_add(request):
    service_types = Service.SERVICE_TYPES  
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            new_service = form.save(commit=False) 
            
            if Service.objects.filter(service_type=new_service.service_type, active=True).exists():
                form.add_error('service_type', 'Error: Service already exists.')
                context = {
                    'form': form,
                    'service_types': service_types,
                }
                return render(request, 'services_add.html', context)
            
            new_service.save()  
            return redirect('service-list-page')
    else:
        form = ServiceForm()

    context = {
        'form': form,
        'service_types': service_types,
    }

    return render(request, 'services_add.html', context)

@staff_required
@login_required
def service_update(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if service.active is False:
        return redirect('service-list-page')

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service-update-page', service_id=service.id)
    else:
        form = ServiceForm(instance=service)

    return render(request, 'services_update.html', {'form': form, 'service': service})

@staff_required
@login_required
def service_delete(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.active = False
        service.save()
        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})
