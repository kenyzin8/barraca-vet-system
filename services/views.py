from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Service
from django.http import JsonResponse
from .forms import ServiceForm

@staff_required
@login_required
def service_list(request):
    services = Service.objects.order_by('-id')
    context = {'services': services}
    return render(request, 'services_list.html', context)

@staff_required
@login_required
def service_add(request):
    service_types = Service.SERVICE_TYPES  
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
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
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service-list-page')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'services_update.html', {'form': form, 'service': service})

@staff_required
@login_required
def service_product(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.delete()
        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})