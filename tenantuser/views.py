from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(reqeust):
    return HttpResponse(f"<h1> {reqeust.tenant.name}'s domain")