"""brokeSpoke URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout', include('dashboard.urls')),
    path('signout/<int:id>/', include('dashboard.urls')),
    path('', include('dashboard.urls')),
    path('dashboard', include('dashboard.urls')),
    path('people', include('dashboard.urls')),
    path('people/new', include('dashboard.urls')),
    path('timelogs', include('dashboard.urls')),
    path('timelogs/new', include('dashboard.urls')),
    path('transactions', include('dashboard.urls')),
    path('transactions/new', include('dashboard.urls')),
    path('users', include('dashboard.urls'))
]
