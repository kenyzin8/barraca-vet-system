from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/services/', views.service_list, name='service-list-page'),
    path('admin/services/add/', views.service_add, name='service-add-page'),
    path('admin/services/update/<int:service_id>/', views.service_update, name='service-update-page'),
    path('admin/services/delete/<int:service_id>/', views.service_product, name='delete-service-page'),
]