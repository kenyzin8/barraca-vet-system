from django.shortcuts import render
from .decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Notification, Province, Municipality, Barangay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from record_management.models import Client
from django.db.models import Q

@staff_required
@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(is_active=True).order_by('-date_created')[:5]
    notifications_list = list(notifications.values())
    return JsonResponse(notifications_list, safe=False)

def handler403(request, exception):
    return render(request, '404.html', {}, status=403)

def handler404(request, exception):
    return render(request, '404.html', {}, status=404)

def handler500(request):
    return render(request, '404.html', {}, status=500)

@csrf_exempt
def test(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            user = User.objects.filter(Q(email=email) | Q(client__contact_number=phone), client__isBanned=True).first()

            if user:
                return JsonResponse({'result': 'Your account is banned. Please contact the administrator.'})
            else:
                return JsonResponse({'result': 'Your account is not banned.'})

            return JsonResponse({'result': user.client.full_name, 'email': user.email, 'phone': user.client.contact_number})
        except Exception as e:
            return JsonResponse({'result': str(e)})

def get_municipalities(request):
    province_id = request.GET.get('province_id')
    municipalities = Municipality.objects.filter(province_id=province_id)
    data = [{'id': m.id, 'name': m.name} for m in municipalities]
    return JsonResponse(data, safe=False)

def get_barangays(request):
    municipality_id = request.GET.get('municipality_id')
    barangays = Barangay.objects.filter(municipality_id=municipality_id)
    data = [{'id': b.id, 'name': b.name} for b in barangays]
    return JsonResponse(data, safe=False)