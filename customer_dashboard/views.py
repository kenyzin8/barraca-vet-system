from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from record_management.models import Pet

# Create your views here.
@login_required
def customer_dashboard(request):
    pets = Pet.objects.filter(client=request.user.client, is_active=True).order_by('-id')[:3]
    context = {"pets": pets}
    return render(request, 'customer_dashboard.html', context)