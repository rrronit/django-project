from django.urls import path
from . import views
from django.contrib.auth import views as vv



urlpatterns = [
    path('register/',views.register),
    path('login/',views.login),
    
]
