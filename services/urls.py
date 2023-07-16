from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('admin/services/', permission_required('services.add_service', raise_exception=True)(views.service_list), name='service-list-page'),
    path('admin/services/add/', permission_required('services.add_service', raise_exception=True)(views.service_add), name='service-add-page'),
    path('admin/services/update/<int:service_id>/', permission_required('services.add_service', raise_exception=True)(views.service_update), name='service-update-page'),
    path('admin/services/delete/<int:service_id>/', permission_required('services.add_service', raise_exception=True)(views.service_delete), name='delete-service-page'),
]