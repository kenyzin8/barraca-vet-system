import datetime

from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Product, ProductType
from .forms import ProductForm
from django.http import JsonResponse
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt

@staff_required
@login_required
def product_list(request):
    products = Product.objects.order_by('-id')
    today = datetime.date.today()
    context = {'products': products, 'today': today}
    return render(request, 'inventory_list.html', context)

@staff_required
@login_required
def product_type_list(request):
    product_types = ProductType.objects.order_by('-id')
    context = {'product_types': product_types}
    return render(request, 'product_type_list.html', context)

@staff_required
@login_required
@csrf_exempt
def add_type_page(request):   
    if request.method == 'POST':
        name = request.POST.get('type_name') 
        ProductType.objects.create(name=name)
        return JsonResponse({'result': 'success'})

# missing update

@staff_required
@login_required
@csrf_exempt
def delete_type_page(request, type_id):
    try:
        product_type = ProductType.objects.get(pk=type_id)
        product_type.delete()
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
            form.save()
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
    previous_batch_numbers = list(Product.objects.values_list('batch_number', flat=True).distinct())

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product-list-page')
        else:
            print(form.errors)     
    else:
        form = ProductForm(instance=product)

    return render(request, 'inventory_update.html', {'form': form, 'previous_batch_numbers': previous_batch_numbers, 'product': product})

@staff_required
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.delete()
        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'message': 'Invalid request method'})

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

@staff_required
@login_required
def reorder_list(request):
    products = Product.objects.filter(quantity_on_stock__lte=F('critical_level')).order_by('-id')
    context = {'products': products}
    return render(request, 'reorder_list.html', context)