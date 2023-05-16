from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('register/', views.register_user, name='register-user-page'),
    path('client/account-settings/', views.client_profile_view, name='client-account-settings-page'),
    path('my-pets/', views.pet_list, name='pet-list-page'),
    path('register-pet/', views.register_pet, name='register-pet-page'),
    path('my-pets/view-pet/<int:pet_id>/', views.view_pet, name='view-pet-page'),
    path('my-pets/update-pet/<int:pet_id>/', views.update_pet, name='update-pet-page'),
    path('my-pets/delete-pet/<int:pet_id>/', views.delete_pet, name='delete-pet-page'),
    path('login/', views.login_view, name='login-page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout-page'),
    path('otp/', views.otp_view, name='otp_view'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),

    #BACKEND-ADMIN-SIDE
    path('admin/account-settings/', views.admin_profile_view, name='admin-account-settings-page'),
    path('admin/client-list/', views.client_module, name='admin-client-list-page'),
    path('admin/client-list/view-client/<int:client_id>/', views.admin_view_client, name='admin-view-client-page'),
    path('admin/pet-list/', views.pet_module, name='admin-pet-list-page'),
    path('admin/pet-list/view-pet/<int:pet_id>/', views.admin_view_pet, name='admin-view-pet-page'),
    path('admin/pet-list/update-pet/<int:pet_id>/', views.admin_update_pet, name='admin-update-pet-page'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # path('register/client/', views.register_client, name='register-client-page'),
    #path('register/cancel/', views.cancel_registration, name='cancel-registration-page'), 
    #path('success/', views.registration_success, name='client-success-page'),