from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Service
from django.http import JsonResponse
from .forms import ServiceForm

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
            new_service.original_service_type = new_service.service_type 
            new_service.previous_version = "New"
            new_service.updated_version = "New"
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

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            new_service_type = form.cleaned_data['service_type'] if form.cleaned_data['service_type'] != service.service_type else None
            new_fee = form.cleaned_data['fee'] if form.cleaned_data['fee'] != service.fee else None
            new_remarks = form.cleaned_data['remarks'] if form.cleaned_data['remarks'] != service.remarks else None

            new_service = service.create_new_version(new_service_type, new_fee, new_remarks)

            return redirect('service-list-page')
    else:
        form = ServiceForm(initial={'fee': service.fee, 'service_type': service.service_type, 'remarks': service.remarks})

    previous_services = Service.objects.filter(original_service_type=service.original_service_type).order_by('-control_number')

    return render(request, 'services_update.html', {'form': form, 'service': service, 'previous_services': previous_services})

@staff_required
@login_required
def service_product(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.delete()
        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})