from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('user/login/', views.user_login, name='login'),
    path('user/register/', views.user_register, name='register'),
]
