from django.urls import include, path
from .views import PetAPIView, APILoginView

urlpatterns = [
    path('get-pet/', PetAPIView.as_view(), name='get-pet-page'),
    path('mobile-login/', APILoginView.as_view(), name='mobile-login-page')
]
