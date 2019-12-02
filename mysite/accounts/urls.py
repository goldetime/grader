from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'accounts'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
] 
