from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('register/', views.register_user, name='register-user-page'),
    path('forgot-password/step-1/', views.forgot_password, name='forgot-password-page'),
    path('forgot-password/step-3/', views.forgot_password_step_3, name='forgot-password-step-3-page'),
    path('client/account-settings/', views.client_profile_view, name='client-account-settings-page'),
    path('client/password-settings/', views.client_change_password_view, name='client-password-settings-page'),
    path('client/otp-settings/', views.client_change_otp_view, name='client-otp-settings-page'),
    path('my-pets/', views.pet_list, name='pet-list-page'),
    path('register-pet/', views.register_pet, name='register-pet-page'),
    path('my-pets/view-pet/<int:pet_id>/', views.view_pet, name='view-pet-page'),
    path('my-pets/update-pet/<int:pet_id>/', views.update_pet, name='update-pet-page'),
    path('my-pets/delete-pet/<int:pet_id>/', views.delete_pet, name='delete-pet-page'),
    path('login/', views.login_view, name='login-page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout-page'),
    path('otp/', views.otp_view, name='otp_view'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('does_pet_have_appointment/<int:pet_id>/', views.does_pet_have_appointment, name='does_pet_have_appointment'),
    #BACKEND-ADMIN-SIDE
    path('admin/account-settings/', views.admin_profile_view, name='admin-account-settings-page'),
    path('admin/password-settings/', views.admin_change_password_view, name='admin-password-settings-page'),
    path('admin/otp-settings/', views.admin_change_otp_view, name='admin-otp-settings-page'),
    path('admin/client-list/', permission_required('record_management.add_client', raise_exception=True)(views.client_module), name='admin-client-list-page'),
    path('admin/client-list/view-client/<int:client_id>/', permission_required('record_management.add_client', raise_exception=True)(views.admin_view_client), name='admin-view-client-page'),
    path('admin/pet-list/', permission_required('record_management.add_pet', raise_exception=True)(views.pet_module), name='admin-pet-list-page'),
    path('admin/pet-list/view-pet/<int:pet_id>/', permission_required('record_management.add_pet', raise_exception=True)(views.admin_view_pet), name='admin-view-pet-page'),
    path('admin/pet-list/update-pet/<int:pet_id>/', permission_required('record_management.add_pet', raise_exception=True)(views.admin_update_pet), name='admin-update-pet-page'),
    path('admin/pet-consultation/', permission_required('record_management.add_pet', raise_exception=True)(views.medical_record), name='admin-medical-record-page'),
    path('admin/submit-consultation/', permission_required('record_management.add_pet', raise_exception=True)(views.SubmitConsultationView.as_view()), name='admin-submit-consultation-page'),
    path('admin/view-prescription/<int:prescription_id>/', permission_required('record_management.add_pet', raise_exception=True)(views.view_prescription), name='admin-view-prescription-page'),
    path('admin/upload-lab-image/', permission_required('record_management.add_pet', raise_exception=True)(views.LabResultImageUploadView.as_view()), name='admin-upload-lab-image-page'),
    path('admin/add-pet-medical-prescription/', permission_required('record_management.add_pet', raise_exception=True)(views.add_medical_prescription), name='admin-add-pet-medical-prescription-page'),
    path('admin/add-pet-medical-prescription/submit/', permission_required('record_management.add_pet', raise_exception=True)(views.SubmitPrescription.as_view()), name='admin-submit-pet-medical-prescription-page'),
    path('admin/add-pet-health-card-treatment/', permission_required('record_management.add_pet', raise_exception=True)(views.add_health_card_treatment), name='admin-add-pet-health-card-treatment-page'),
    path('admin/add-pet-health-card-treatment/submit/', permission_required('record_management.add_pet', raise_exception=True)(views.SubmitHealthCardTreatment.as_view()), name='admin-submit-pet-health-card-treatment-page'),
    path('admin/get-laboratory-results-image/<int:treatmentID>/', permission_required('record_management.add_pet', raise_exception=True)(views.get_laboratory_results_data), name='admin-get-laboratory-results-data-page'),
    path('admin/update-consultation/<int:treatmentID>/', permission_required('record_management.add_pet', raise_exception=True)(views.update_medical_record), name='admin-update-consultation-page'),
    path('admin/update-consultation/submit/', permission_required('record_management.add_pet', raise_exception=True)(views.UpdateConsultationView.as_view()), name='admin-submit-update-consultation-page'),
    path('admin/delete-consultation/<int:treatmentID>/', permission_required('record_management.add_pet', raise_exception=True)(views.delete_treatment), name='admin-delete-consultation-page'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # path('register/client/', views.register_client, name='register-client-page'),
    #path('register/cancel/', views.cancel_registration, name='cancel-registration-page'), 
    #path('success/', views.registration_success, name='client-success-page'),