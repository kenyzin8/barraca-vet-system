from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about-page'),
    path('contact/', views.contact, name='contact-page'),
    path('pricing/', views.pricing, name='pricing-page'),
]
