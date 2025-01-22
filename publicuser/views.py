from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.

def index(request):
    return redirect('login')

def user_register(request):
    return render(request, 'public/register_form.html')

def user_login(request):
    return render(request, 'public/login.html')