from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('user/login/', views.user_login, name='login'),
    path('user/register/', views.user_register, name='register'),
    path('user/logout/', views.user_logout, name='logout'),
    path('user/dashboard/', views.dashboard, name='dashboard'),
    path('user/requests/', views.user_requests, name='requests'),
    path('user/requests/details/<str:uid>/', views.requested_details, name='requested_details'),
]
