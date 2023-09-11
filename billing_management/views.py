from django.shortcuts import render, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from inventory.models import Product, ProductType
from services.models import Service
from record_management.models import Client
from .models import Billing, BillingProduct, BillingService, format_billing_number
from django.db.models import Max
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.models import User
from django.db import transaction
from uuid import uuid4
import json
from datetime import datetime, timedelta, time

@login_required
@staff_required
def bill(request):

    client_id = request.GET.get('to', None)

    if client_id is not None:
        client = Client.objects.get(id=client_id)
    else:
        client = None

    services = Service.objects.filter(active=True)
    clients = Client.objects.filter(user__is_active=True)
    clients_count = clients.count()

    types = ProductType.objects.all()
    product_dict = {t.name.replace(' ', '-'): Product.objects.filter(type=t, quantity_on_stock__gt=0) for t in types}
    
    last_bill = Billing.objects.aggregate(Max('id'))['id__max']
    next_bill_number = format_billing_number((last_bill + 1) if last_bill else 1)

    selected_medicines = []
    selected_service = -1

    if 'selected_medicines' in request.session:
        selected_medicines = request.session.get('selected_medicines', [])

    if 'selected_service' in request.session:
        selected_service = request.session.get('selected_service', -1)

    context = {
        'client': client,
        'clients_count': clients_count,
        'product_dict': product_dict,
        'products_count': Product.objects.count(),
        'services': services,
        'services_count': services.count(),
        'clients': clients,
        'next_bill_number': next_bill_number
    }

    if selected_medicines:
        context.update({'selected_medicines': selected_medicines})
        del request.session['selected_medicines']

    if selected_service != -1:
        context.update({'selected_service': selected_service})
        del request.session['selected_service']

    return render(request, 'billing.html', context)

# @staff_required
# @login_required
# def bill_client(request):
#     client_id = request.GET.get('to', None)
#     if client_id is not None:
#         client = Client.objects.get(id=client_id)
#     else:
#         client = None
#     products = Product.objects.all()
#     services = Service.objects.all()
#     clients = Client.objects.all()

#     last_bill = Billing.objects.aggregate(Max('id'))['id__max']
#     next_bill_number = (last_bill + 1) if last_bill else 1

#     context = {
#         'client': client,
#         'products': products,
#         'services': services,
#         'clients': clients,
#         'next_bill_number': next_bill_number
#     }
#     return render(request, 'billing.html', context)

@csrf_exempt
@staff_required
@login_required
def post_bill(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)

    if not request.body:
        return JsonResponse({'status': 'error', 'message': 'Empty request body.'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)

    if request.method == 'POST':
        data = json.loads(request.body)
        client_id = data.get('client_id', None)
        full_name = data.get('full_name', "Walk-in Customer")
        service_ids = data.get('service_ids', [])
        product_ids_and_quantities = data.get('product_ids', [])

        if client_id is None:
            with transaction.atomic():
                username = "walkin_" + str(uuid4())
                user = User(username=username, is_active=False)
                user.save()

                client = Client(user=user, first_name=full_name, last_name="(walk-in)", address="N/A", contact_number="N/A")
                client.save()
        else:
            client = Client.objects.get(pk=client_id)

        services = Service.objects.filter(id__in=service_ids)
        products = [Product.objects.get(id=pq['id']) for pq in product_ids_and_quantities]

        bill = Billing(client=client, date_created=timezone.now())
        bill.save()

        for pq in product_ids_and_quantities:
            product = Product.objects.get(id=pq['id'])
            billing_product = BillingProduct(billing=bill, product=product, quantity=pq['quantity'])
            billing_product.save()
            product.quantity_on_stock -= Decimal(pq['quantity'])
            product.save()

        for service in services:
            billing_service = BillingService(billing=bill, service=service)
            billing_service.save()

        bill.services.set(services)
        bill.products.set(products)

        return JsonResponse({'status': 'success'}, status=200)

@staff_required
@login_required
def view_bill(request, bill_id):
    bill = get_object_or_404(Billing, pk=bill_id)
    context = {'bill': bill}
    return render(request, 'view_bill.html', context)

@login_required
@staff_required
def sales(request):
    bills = Billing.objects.all().order_by('-id')

    startDateStr = request.GET.get('startDate')
    endDateStr = request.GET.get('endDate')

    gross_revenue = 0

    if startDateStr and endDateStr:
        startDate = datetime.strptime(startDateStr, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDateStr, '%Y-%m-%d').date()

        endDate = endDate + timedelta(days=1) - timedelta(seconds=1)
        
        bills = bills.filter(date_created__range=[startDate, endDate])
    else:
        current_date = datetime.now().date()
        start_of_day = datetime.combine(current_date, time.min)
        end_of_day = datetime.combine(current_date, time.max)
        
        bills = bills.filter(date_created__range=[start_of_day, end_of_day])

    bills = bills.prefetch_related('products', 'services')
    
    for bill in bills:
        gross_revenue += bill.get_total()

    context = {'bills': bills, 'gross_revenue': gross_revenue}
    return render(request, 'sales.html', context)

# @csrf_exempt
# @staff_required
# @login_required
# def post_bill(request):
#     if request.method == 'POST':
#         client_id = request.POST.get('client_id')
#         service_ids = request.POST.getlist('service_ids[]')
#         product_ids = request.POST.getlist('product_ids[]')
#         quantities = request.POST.getlist('quantities[]')

#         client = Client.objects.get(pk=client_id)
#         services = Service.objects.filter(id__in=service_ids)
#         products = Product.objects.filter(id__in=product_ids)

#         bill = Billing(client=client, date_created=timezone.now())
#         bill.save()

#         for product, quantity in zip(products, quantities):
#             billing_product = BillingProduct(billing=bill, product=product, quantity=quantity)
#             billing_product.save()
#             # reduce the quantity on hand of the product
#             product.quantity_on_stock -= Decimal(quantity)
#             product.save()

#         bill.services.set(services)
#         bill.products.set(products)

#         # Send response back to AJAX function
#         return JsonResponse({'status': 'success'}, status=200)
