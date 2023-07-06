from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Service
from django.http import JsonResponse
from .forms import ServiceForm
from django.db.models import Q

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
            new_service.previous_version = "New"
            new_service.updated_version = "New"
            
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

    if Service.objects.filter(id=service_id, active=False).exists():
        return redirect('service-list-page')

    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            new_service_type = form.cleaned_data['service_type'] 
            new_fee = form.cleaned_data['fee'] 
            new_remarks = form.cleaned_data['remarks'] 

            if new_service_type != service.service_type and Service.objects.filter(service_type=new_service_type, active=True).exists():
                form.add_error('service_type', 'Error: Service already exists.')
                if service.original_service is None:
                    previous_services = Service.objects.filter(Q(id=service.id) | Q(original_service=service)).order_by('-control_number')
                else:
                    previous_services = Service.objects.filter(Q(id=service.original_service.id) | Q(original_service=service.original_service)).order_by('-control_number')
                return render(request, 'services_update.html', {'form': form, 'service': service, 'previous_services': previous_services})

            new_service = service.create_new_version(new_service_type if new_service_type != service.service_type else None, 
                                                     new_fee if new_fee != service.fee else None, 
                                                     new_remarks if new_remarks != service.remarks else None)

            return redirect('service-update-page', service_id=new_service.id)
    else:
        form = ServiceForm(initial={'fee': service.fee, 'service_type': service.service_type, 'remarks': service.remarks})

    if service.original_service is None:
        previous_services = Service.objects.filter(Q(id=service.id) | Q(original_service=service)).order_by('-control_number')
    else:
        previous_services = Service.objects.filter(Q(id=service.original_service.id) | Q(original_service=service.original_service)).order_by('-control_number')

    return render(request, 'services_update.html', {'form': form, 'service': service, 'previous_services': previous_services})

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
