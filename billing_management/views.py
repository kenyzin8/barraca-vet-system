from django.shortcuts import render, get_object_or_404, redirect
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from inventory.models import Product, ProductType
from services.models import Service
from record_management.models import Client
from .models import Billing, BillingProduct, BillingService, format_billing_number
from django.db.models import Max, Count, Min, OuterRef, Subquery, Q, F
from django.utils.timezone import now
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.models import User
from django.db import transaction
from uuid import uuid4

import json

from datetime import datetime, timedelta, time, date

def format_volume(volume):
    if volume % 1 == 0:
        return str(int(volume))
    return str(volume)

@login_required
@staff_required
def bill(request):

    client_id = request.GET.get('to', None)

    if client_id is not None:
        client = Client.objects.get(id=client_id)
    else:
        client = None

    services = Service.objects.filter(active=True).exclude(fee__lte=0)
    clients = Client.objects.filter(user__is_active=True)
    clients_count = clients.count()

    types = ProductType.objects.all().filter(active=True)
    # product_dict = {t.name.replace(' ', '-'): Product.objects.filter(type=t, quantity_on_stock__gt=0, active=True) for t in types}
    #product_dict = {t.name.replace(' ', '-'): Product.objects.filter(type=t, quantity_on_stock__gt=0, active=True, expiration_date__gt=date.today()) for t in types}
    # product_dict = {}
    # for product_type in types:
    #     oldest_products = (Product.objects
    #                     .filter(type=product_type, quantity_on_stock__gt=0, active=True, expiration_date__gt=now())
    #                     .order_by('product_name', 'date_added')
    #                     .distinct('product_name'))
        
    #     oldest_product_ids = [product.id for product in oldest_products]
        
    #     products = Product.objects.filter(id__in=oldest_product_ids)
        
    #     product_dict[product_type.name.replace(' ', '-')] = products
    product_dict = {}
    for product_type in types:
        valid_products = Product.objects.filter(
            type=product_type, 
            quantity_on_stock__gt=0, 
            active=True, 
            expiration_date__gt=timezone.now().date()
        )

        final_products = {}
        processed_product_names = set()

        for product in valid_products.order_by('date_added'):
            product_name = product.product_name

            if product_name in processed_product_names:
                continue

            batch = valid_products.filter(product_name=product_name).first()

            while batch and batch.quantity_on_stock <= batch.critical_level:
                key = f"{product_name}-{batch.batch_number}"
                final_products[key] = batch
                next_batch = valid_products.filter(
                    product_name=product_name, 
                    date_added__gt=batch.date_added
                ).first()
                batch = next_batch

            if batch and batch.quantity_on_stock > 0:
                key = f"{product_name}-{batch.batch_number}"
                final_products[key] = batch

            processed_product_names.add(product_name)

        product_dict[product_type.name.replace(' ', '-')] = list(final_products.values())
        
    for type_key, products in product_dict.items():
        for product in products:
            product.formatted_volume = format_volume(product.volume)

    last_bill = Billing.objects.aggregate(Max('id'))['id__max']
    next_bill_number = format_billing_number((last_bill + 1) if last_bill else 1)

    selected_medicines = []
    selected_service = -1

    if 'selected_medicines' in request.session:
        selected_medicines = request.session.get('selected_medicines', [])

    if 'selected_service' in request.session:
        selected_service = request.session.get('selected_service', -1)

    if 'selected_services' in request.session:
        selected_services = request.session.get('selected_services', [])

    pending_payments_bills = Billing.objects.filter(isActive=True, isPaid=False).order_by('-id')

    context = {
        'client': client,
        'clients_count': clients_count,
        'product_dict': product_dict,
        'products_count': Product.objects.count(),
        'services': services,
        'services_count': services.count(),
        'clients': clients,
        'next_bill_number': next_bill_number,
        'pending_payments_bills': pending_payments_bills
    }

    if selected_medicines:
        context.update({'selected_medicines': selected_medicines})
        del request.session['selected_medicines']

    if selected_service != -1:
        context.update({'selected_service': selected_service})
        del request.session['selected_service']

    if 'selected_services' in request.session:
        selected_services = request.session.get('selected_services', [])
        for selected_service in selected_services:
            service_id = selected_service['id']
            service = Service.objects.filter(id=service_id)
            services = services | service

        context.update({'selected_services': selected_services})

        del request.session['selected_services']
    
    context['services'] = services
    bill_to_process = None
    if 'bill_to_process' in request.session:
        bill_to_process = request.session.get('bill_to_process')
        context.update({'bill_to_process': bill_to_process})
        del request.session['bill_to_process']

    context.update({'bill_number_to_view': bill_to_process.strip() if bill_to_process else next_bill_number})

    if 'selected_pet_owner_id' in request.session:
        context.update({'selected_pet_owner_id': request.session.get('selected_pet_owner_id')})
        selected_pet_owner_id_name = Client.objects.get(id=request.session.get('selected_pet_owner_id')).full_name
        context.update({'selected_pet_owner_id_name': selected_pet_owner_id_name})
        del request.session['selected_pet_owner_id']

    return render(request, 'billing.html', context)

@staff_required
@login_required
def cancel_bill(request):
    try:
        if 'selected_medicines' in request.session:
            del request.session['selected_medicines']

        if 'selected_service' in request.session:
            del request.session['selected_service']

        if 'selected_services' in request.session:
            del request.session['selected_services']

        if 'selected_pet_owner_id' in request.session:
            del request.session['selected_pet_owner_id']

        if 'bill_to_process' in request.session:
            del request.session['bill_to_process']

        return JsonResponse({'status': 'success'}, status=200)
    except KeyError:
        return JsonResponse({'status': 'error'}, status=400)
    
@staff_required
@login_required
def process_unpaid_bill(request):
    if request.method == 'POST':
        bill_id = request.POST.get('bill_id')
        bill = get_object_or_404(Billing, pk=bill_id)
        
        medicines = []
        services = []
        for b in bill.billing_products.all():
            medicines.append({
                'id': b.product.id,
                'details': {
                    'quantity': int(b.quantity),
                }
            })
        
        for b in bill.billing_services.all():
            services.append({
                'id': b.service.id,
                'details':{
                    'quantity': int(b.quantity),
                }
            })
        
        request.session['selected_medicines'] = medicines
        request.session['selected_services'] = services
        request.session['selected_pet_owner_id'] = bill.client.id
        request.session['bill_to_process'] = bill.get_billing_number()

        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'status': 'error'}, status=400)

@staff_required
@login_required
def mark_unpaid_bill_as_paid(request):
    if request.method == 'POST':
        bill_id = request.POST.get('bill_id')
        bill = get_object_or_404(Billing, pk=bill_id)
        
        bill.isPaid = True
        bill.date_created = timezone.now()
        bill.save()

        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'status': 'error'}, status=400)

@staff_required
@login_required
def cancel_unpaid_bill(request):
    if request.method == 'POST':
        bill_id = request.POST.get('bill_id')
        bill = get_object_or_404(Billing, pk=bill_id)
        
        bill.isActive = False
        bill.save()

        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'status': 'error'}, status=400)

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

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)

    client_id = data.get('client_id')
    full_name = data.get('full_name', "Walk-in Customer")
    bill_to_process = data.get('bill_to_process')

    if client_id is not None:
        client = get_object_or_404(Client, pk=client_id)
    else:
        username = "walkin_" + str(uuid4())
        user = User.objects.create(username=username, is_active=False)
        client = Client.objects.create(user=user, first_name=full_name, last_name="(walk-in)", gender="None",
                                       street="N/A", barangay="N/A", city="N/A", province="N/A", contact_number="N/A")

    if bill_to_process:
        bill = get_object_or_404(Billing, pk=bill_to_process)
    else:
        bill = Billing.objects.create(client=client, isActive=True, isPaid=False)

    product_ids_and_quantities = data.get('product_ids', [])
    current_products = {bp.product.id: bp for bp in BillingProduct.objects.filter(billing=bill)}
    for pq in product_ids_and_quantities:
        product = get_object_or_404(Product, pk=pq['id'])
        quantity = pq.get('quantity', 1)
        if product.id in current_products:
            billing_product = current_products.pop(product.id)
            billing_product.quantity = quantity
            billing_product.save()
        else:
            BillingProduct.objects.create(billing=bill, product=product, quantity=quantity)
        product.quantity_on_stock -= Decimal(quantity)
        product.save()

    # Remove products not in the incoming data
    for product_id, billing_product in current_products.items():
        billing_product.delete()

    service_ids_and_quantities = data.get('service_ids', [])
    current_services = {bs.service.id: bs for bs in BillingService.objects.filter(billing=bill)}
    for sq in service_ids_and_quantities:
        service = get_object_or_404(Service, pk=sq['id'])
        quantity = sq.get('quantity', 1)
        if service.id in current_services:
            billing_service = current_services.pop(service.id)
            billing_service.quantity = quantity
            billing_service.save()
        else:
            BillingService.objects.create(billing=bill, service=service, quantity=quantity)

    # Remove services not in the incoming data
    for service_id, billing_service in current_services.items():
        billing_service.delete()

    bill.isActive = True
    bill.isPaid = True
    bill.date_created = timezone.now()
    bill.save()

    for key in ['selected_medicines', 'selected_service', 'selected_services', 'selected_pet_owner_id', 'bill_to_process']:
        request.session.pop(key, None)

    return JsonResponse({'status': 'success'}, status=200)


@login_required
@staff_required
def view_bill(request, bill_id):
    bill = get_object_or_404(Billing, pk=bill_id)
    
    if not bill.isPaid:
        return redirect('unpaid-bill-page', bill_id=bill_id)

    bill_data = []

    for b in bill.billing_products.all():
        bill_data.append({
            'type': 'Product',
            'particulars': b.product.product_name,
            'qty': str(b.quantity),
            'amount': str(b.price_at_time_of_purchase), 
            'amount_total': str(b.quantity * b.price_at_time_of_purchase)  
        })

    for b in bill.billing_services.all():
        bill_data.append({
            'type': 'Service',
            'particulars': b.service.service_type,
            'qty': str(b.quantity), 
            'amount': str(b.price_at_time_of_purchase),
            'amount_total': str(b.price_at_time_of_purchase * b.quantity)
        })

    context = {'bill': bill, 'bill_data': bill_data}
    return render(request, 'view_bill.html', context)

@login_required
@staff_required
def view_unpaid_bill(request, bill_id):
    bill = get_object_or_404(Billing, pk=bill_id)
    
    if bill.isPaid:
        return redirect('view-bill-page', bill_id=bill_id)

    if not bill.isActive:
        return redirect('sales-page')
    
    bill_data = []

    for b in bill.billing_products.all():
        bill_data.append({
            'type': 'Product',
            'particulars': b.product.product_name,
            'qty': str(b.quantity),
            'amount': str(b.price_at_time_of_purchase), 
            'amount_total': str(b.quantity * b.price_at_time_of_purchase)  
        })

    for b in bill.billing_services.all():
        bill_data.append({
            'type': 'Service',
            'particulars': b.service.service_type,
            'qty': str(b.quantity), 
            'amount': str(b.price_at_time_of_purchase),
            'amount_total': str(b.price_at_time_of_purchase * b.quantity)
        })

    context = {'bill': bill, 'bill_data': bill_data}
    return render(request, 'view_unpaid_bill.html', context)

def custom_format(number):
    if number == int(number):
        return "{:.2f}".format(number)
    else:
        return str(number).rstrip('0').rstrip('.') if '.' in str(number) else str(number)

def get_range_name(start_date_str, end_date_str, current_year):
    today = datetime.today().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    month_start = datetime(current_year, today.month, 1).date()
    month_end = (datetime(current_year, today.month + 1, 1) - timedelta(days=1)).date()

    year_start = datetime(current_year, 1, 1).date()
    year_end = datetime(current_year, 12, 31).date()

    lifetime_start = datetime(2010, 1, 1).date()
    lifetime_end = year_end

    if start_date_str == today and end_date_str == today:
        return "Today (" + start_date_str.strftime("%B %d, %Y") + ")"
    elif start_date_str == week_start and end_date_str == week_end:
        return "This Week (" + start_date_str.strftime("%B %d") + " - " + end_date_str.strftime("%B %d, %Y") + ")"
    elif start_date_str == month_start and end_date_str == month_end:
        return "This Month (" + start_date_str.strftime("%B %Y") + ")"
    elif start_date_str == year_start and end_date_str == year_end:
        return "Year (" + start_date_str.strftime("%Y") + ")"
    elif start_date_str == lifetime_start and end_date_str == lifetime_end:
        return "Lifetime"
    else:
        return start_date_str.strftime("%B %d, %Y") + " - " + end_date_str.strftime("%B %d, %Y")

@login_required
@staff_required
def sales(request):
    bills = Billing.objects.all().filter(isActive=True, isPaid=True).order_by('-id')

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

    total_products_count = sum(bill.billing_products.all().count() for bill in bills)
    total_services_count = sum(bill.billing_services.all().count() for bill in bills)

    billing_services_data = []
    billing_products_data = []

    services_sub_total = 0
    products_sub_total = 0

    for bill in bills.order_by('id'):
        _date = bill.date_created.strftime("%b %d, %Y %I:%M %p")
        for bs in bill.billing_services.all():
            total = bs.quantity * bs.price_at_time_of_purchase
            billing_services_data.append({
                'id': bill.get_billing_number(),
                'date_created': _date,
                'service': bs.service.service_type,
                'quantity': int(bs.quantity),
                'sold_under': bill.client.full_name,
                'price': custom_format(bs.price_at_time_of_purchase),
                'total_due': custom_format(total)
            })
            
            services_sub_total += total

        for bp in bill.billing_products.all():
            total = bp.quantity * bp.price_at_time_of_purchase
            billing_products_data.append({
                'id': bill.get_billing_number(),
                'date_created': _date,
                'product': bp.product.product_name,
                'quantity': int(bp.quantity),
                'sold_under': bill.client.full_name,
                'price': custom_format(bp.price_at_time_of_purchase),
                'total_due': custom_format(total)
            })

            products_sub_total += total

    # gross_revenue = services_sub_total + products_sub_total

    _range = "Today (" + datetime.now().strftime("%B %d, %Y") + ")"

    if startDateStr and endDateStr:
        startDateStr_obj = datetime.strptime(startDateStr, '%Y-%m-%d').date()
        endDateStr_obj = datetime.strptime(endDateStr, '%Y-%m-%d').date()
        _range = get_range_name(startDateStr_obj, endDateStr_obj, datetime.now().year)

    context = {
        'bills': bills,
        'gross_revenue': custom_format(gross_revenue), 
        'total_products_count': total_products_count, 
        'total_services_count': total_services_count,
        'billing_services_data': billing_services_data,
        'billing_products_data': billing_products_data,
        'range': _range,
        'services_sub_total': custom_format(services_sub_total),
        'products_sub_total': custom_format(products_sub_total)
        }

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
