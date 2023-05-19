from django.shortcuts import render, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from inventory.models import Product
from services.models import Service
from record_management.models import Client
from .models import Billing, BillingProduct
from django.db.models import Max
from django.utils import timezone

@staff_required
@login_required
def bill(request):
    products = Product.objects.all()
    services = Service.objects.all()
    clients = Client.objects.all()

    last_bill = Billing.objects.aggregate(Max('id'))['id__max']
    next_bill_number = (last_bill + 1) if last_bill else 1

    context = {'products': products, 'services': services, 'clients': clients, 'next_bill_number': next_bill_number}
    return render(request, 'billing.html', context)

@staff_required
@login_required
def bill_client(request, client_id):
    client = Client.objects.get(id=client_id)
    products = Product.objects.all()
    services = Service.objects.all()
    clients = Client.objects.all()

    last_bill = Billing.objects.aggregate(Max('id'))['id__max']
    next_bill_number = (last_bill + 1) if last_bill else 1

    context = {
        'client': client,
        'products': products,
        'services': services,
        'clients': clients,
        'next_bill_number': next_bill_number
    }
    return render(request, 'billing.html', context)

@csrf_exempt
@staff_required
@login_required
def post_bill(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        service_ids = request.POST.getlist('service_ids[]')
        product_ids = request.POST.getlist('product_ids[]')
        quantities = request.POST.getlist('quantities[]')

        client = Client.objects.get(pk=client_id)
        services = Service.objects.filter(id__in=service_ids)
        products = Product.objects.filter(id__in=product_ids)

        bill = Billing(client=client, date_created=timezone.now())
        bill.save()

        for product, quantity in zip(products, quantities):
            billing_product = BillingProduct(billing=bill, product=product, quantity=quantity)
            billing_product.save()

        bill.services.set(services)
        bill.products.set(products)

        # Send response back to AJAX function
        return JsonResponse({'status': 'success'}, status=200)

@staff_required
@login_required
def view_bill(request, bill_id):
    bill = get_object_or_404(Billing, pk=bill_id)
    context = {'bill': bill}
    return render(request, 'view_bill.html', context)

@staff_required
@login_required
def sales(request):
    bills = Billing.objects.all().order_by('-id')
    context = {'bills': bills}
    return render(request, 'sales.html', context)