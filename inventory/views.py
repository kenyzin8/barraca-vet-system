import datetime

from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Product, ProductType, Notification
from .forms import ProductForm
from django.http import JsonResponse
from django.db.models import F, Q
from django.views.decorators.csrf import csrf_exempt
from copy import deepcopy

def format_volume(volume):
    if volume % 1 == 0:
        return str(int(volume))
    return str(volume)

@staff_required
@login_required
def product_list(request):
    products_with_price_changes = Product.objects.none()

    for product in Product.objects.all():
        for change in product.changes_log:
            if 'price' in change:
                products_with_price_changes |= Product.objects.filter(id=product.id)
                break

    for product in products_with_price_changes:
        for change in product.changes_log:
            if 'price' in change:
                old_price, new_price = change['price']
                change_date = change['date']
                update_id = change['update_id']
                #print(f'[{update_id}] - {product.product_name} price changed from {old_price} to {new_price} - Date: {change_date}')

    products = Product.objects.filter(active=True).order_by('-id')

    formatted_products = []
    for product in products:
        product.formatted_volume = format_volume(product.volume)
        formatted_products.append(product)

    today = datetime.date.today()
    context = {'products': formatted_products, 'today': today}
    return render(request, 'inventory_list.html', context)

@staff_required
@login_required
def product_type_list(request):
    product_types = ProductType.objects.filter(active=True).order_by('-id')
    context = {'product_types': product_types}
    return render(request, 'product_type_list.html', context)

@staff_required
@login_required
@csrf_exempt
def add_type_page(request):   
    if request.method == 'POST':
        name = request.POST.get('type_name') 
        #description = request.POST.get('type_description')
        ProductType.objects.create(name=name)
        return JsonResponse({'result': 'success'})

@staff_required
@login_required
def update_type_page(request, type_id):
    try:
        product_type = ProductType.objects.get(pk=type_id)
        if request.method == 'POST':
            name = request.POST.get('type_name') 
            #description = request.POST.get('type_description')
            product_type.name = name
            #product_type.product_type_description = description
            product_type.save()
            return JsonResponse({'result': 'success'})
        else:
            return JsonResponse({'result': 'error', 'message': 'Invalid request method'})
    except ProductType.DoesNotExist:
        return JsonResponse({'result': 'error', 'message': 'Product type does not exist'})

@staff_required
@login_required
@csrf_exempt
def delete_type_page(request, type_id):
    try:
        product_type = ProductType.objects.get(pk=type_id)
        product_type.active = False
        product_type.save()
        return JsonResponse({'result': 'success'})
    except ProductType.DoesNotExist:
        return JsonResponse({'result': 'error', 'message': 'Product type does not exist'})

@staff_required
@login_required
def product_add(request):
    previous_batch_numbers = list(Product.objects.values_list('batch_number', flat=True).distinct())

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.save()  
            return redirect('product-list-page')
        else:
            print(form.errors)
    else:
        form = ProductForm()

    return render(request, 'inventory_add.html', {'form': form, 'previous_batch_numbers': previous_batch_numbers})

@staff_required
@login_required
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.quantity_on_stock = int(product.quantity_on_stock)
    if product.active is False:
        return redirect('product-list-page')

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            old_product = deepcopy(product)
            form.save()

            changes = {}
            for field in form.fields:
                old_value = getattr(old_product, field)
                new_value = getattr(product, field)
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}

            if changes:
                if product.changes_log:
                    product.changes_log.append(changes)
                else:
                    product.changes_log = [changes]
                product.save()

            return redirect('product-update-page', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'inventory_update.html', {'form': form, 'product': product})


# @staff_required
# @login_required
# def product_update(request, product_id):

#     if Product.objects.filter(id=product_id, active=False).exists():
#         return redirect('product-list-page')

#     product = get_object_or_404(Product, id=product_id)
#     previous_batch_numbers = list(Product.objects.values_list('batch_number', flat=True).distinct())

#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             new_product_name = form.cleaned_data['product_name']

#             if new_product_name != product.product_name and Product.objects.filter(product_name=new_product_name, active=True).exists():
#                 form.add_error('product_name', 'Error: Product with this name already exists.')
#                 if product.original_product is None:
#                     previous_products = Product.objects.filter(Q(id=product.id) | Q(original_product=product)).order_by('-batch_number')
#                 else:
#                     previous_products = Product.objects.filter(Q(id=product.original_product.id) | Q(original_product=product.original_product)).order_by('-batch_number')
#                 return render(request, 'inventory_update.html', {'form': form, 'product': product, 'previous_products': previous_products})

#             new_quantity_on_stock = form.cleaned_data['quantity_on_stock'] if form.cleaned_data['quantity_on_stock'] != product.quantity_on_stock else None
#             new_type = form.cleaned_data['type'] if form.cleaned_data['type'] != product.type else None
#             new_manufacturing_date = form.cleaned_data['manufacturing_date'] if form.cleaned_data['manufacturing_date'] != product.manufacturing_date else None
#             new_expiration_date = form.cleaned_data['expiration_date'] if form.cleaned_data['expiration_date'] != product.expiration_date else None
#             new_critical_level = form.cleaned_data['critical_level'] if form.cleaned_data['critical_level'] != product.critical_level else None
#             new_price = form.cleaned_data['price'] if form.cleaned_data['price'] != product.price else None

#             new_product = product.create_new_version(new_product_name, new_quantity_on_stock, new_type, new_manufacturing_date, 
#                                                      new_expiration_date, new_critical_level, new_price)

#             return redirect('product-update-page', product_id=new_product.id)
#     else:
#         form = ProductForm(instance=product)

#     if product.original_product is None:
#         previous_products = Product.objects.filter(Q(id=product.id) | Q(original_product=product)).order_by('-batch_number')
#     else:
#         previous_products = Product.objects.filter(Q(id=product.original_product.id) | Q(original_product=product.original_product)).order_by('-batch_number')

#     return render(request, 'inventory_update.html', {'form': form, 'previous_batch_numbers': previous_batch_numbers, 'product': product, 'previous_products': previous_products})

@staff_required
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.active = False
        product.save()
        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})


@staff_required
@login_required
def reorder_list(request):
    products = Product.objects.filter(quantity_on_stock__lte=F('critical_level'), active=True).order_by('-id')
    
    reorder_data = []

    for product in products:
        reorder_data.append({
            'id': product.id,
            'name': product.product_name,
            'type': product.type.name,
            'form': product.get_form_display(),
            'description': product.product_description,
            'quantity': int(product.quantity_on_stock),
            'critical_level': product.critical_level,
            'price': str(product.price)
        })
    context = {'products': products, 'reorder_data': reorder_data}
    #print(reorder_data)
    return render(request, 'reorder_list.html', context)

@staff_required
@login_required
def check_product_quantity(request, product_id):
    product = Product.objects.get(pk=product_id)
    return JsonResponse({'quantity': float(product.quantity_on_stock)})

@staff_required
@login_required
def check_product_expiry(request, product_id):
    product = Product.objects.get(pk=product_id)
    return JsonResponse({'expiry': product.expiration_date})


from django.core.exceptions import ObjectDoesNotExist

@staff_required
@login_required
def check_product_info(request):
    if request.method == "POST":
        product_ids = request.POST.get('productIds', [])

        response_data = {}

        for product_id in product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                response_data[product_id] = {
                    'quantity': float(product.quantity_on_stock),
                    'expiry': product.expiration_date.strftime('%Y-%m-%d') if product.expiration_date else None
                }
            except ObjectDoesNotExist:
                response_data[product_id] = {
                    'error': f"Product with ID {product_id} not found."
                }

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
