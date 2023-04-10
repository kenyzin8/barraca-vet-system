from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register-user-page'),
    path('register/client/', views.register_client, name='register-client-page'),
    path('register/cancel/', views.cancel_registration, name='cancel-registration-page'), 
    path('success/', views.registration_success, name='client-success-page'),
    path('pet-list/', views.pet_list, name='pet-list-page'),
    path('register-pet/', views.register_pet, name='register-pet-page'),
    path('pet-success/', views.pet_registration_success, name='pet-success-page'),
    path('view-pet/<int:pet_id>/', views.view_pet, name='view-pet-page'),
    path('update-pet/<int:pet_id>/', views.update_pet, name='update-pet-page'),
    path('delete-pet/<int:pet_id>/', views.delete_pet, name='delete-pet-page'),
    path('login/', views.login_view, name='login-page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout-page'),
    path('send_sms/', views.send_sms_to_client, name='send_sms_to_client'),
]
