from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('user/login/', views.user_login, name='login'),
    path('user/register/', views.user_register, name='register'),
    path('user/logout/', views.user_logout, name='logout'),
    path('user/delete/<str:id>/', views.delete_user, name='delete_user'),
    path('user/dashboard/', views.dashboard, name='dashboard'),
    path('user/requests/', views.user_requests, name='requests'),
    path('user/requests/details/<str:uid>/', views.requested_details, name='requested_details'),
    path('users/', views.users, name='users'),
    path('user/<str:uid>/details/', views.user_details, name='user_details'),
    path('user/<str:uid>/tenant/status', views.tenant_status, name='tenant_status'),
    path('user/<str:uid>/update/', views.user_update, name='user_update'),
    path('users/profiles/my-profile', views.profile, name='profile'),
    path('users/profiles/my-profile/', views.save_profile_image, name='save_profile'),
    path('users/<str:uid>/change-password/', views.change_pass, name='change_pass'),
    path('user/paswords/reset/', views.resetPassEmail, name='restPass'),
    path('user/<str:uid>/passwords/reset-password/', views.mail_reset_authentication, name='mail_reset_authentication')
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)