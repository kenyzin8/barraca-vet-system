"""
URL configuration for barraca project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('detailed-admin/', admin.site.urls, name='admin-page'),
    path('', include('record_management.urls')),
    path('', include('frontend.urls')),
    path('', include('admin_dashboard.urls')),
    path('', include('appointment_management.urls')),
    path('', include('customer_dashboard.urls')),
    path('', include('inventory.urls')),
    path('', include('services.urls')),
    path('', include('billing_management.urls')),
]

handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'