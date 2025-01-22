from django.urls import path
from django.contrib.auth import admin
from . import views

urlpatterns = [
    path('', views.index, name='public_home')
]