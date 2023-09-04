from django.urls import path
from .views import *

urlpatterns = [
    path('get-pet/', PetAPIView.as_view(), name='get-pet-page'),
    path('get-token/', TokenGenerator.as_view(), name='get-token-page'),
]
