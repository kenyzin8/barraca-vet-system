from django.shortcuts import render
from .decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.http import JsonResponse

@staff_required
@login_required
def get_notifications(request):
    notifications = Notification.objects.order_by('-date_created')[:5]
    notifications_list = list(notifications.values())
    return JsonResponse(notifications_list, safe=False)

def handler403(request, exception):
    return render(request, '404.html', {}, status=403)

def handler404(request, exception):
    return render(request, '404.html', {}, status=404)

def handler500(request):
    return render(request, '404.html', {}, status=500)