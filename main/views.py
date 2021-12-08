from django.shortcuts import render
from django.http import JsonResponse
from time import sleep

# Create your views here.

def home(request):
    return render(request, "home.html", {})

def test(request):
    sleep(5)
    return JsonResponse({'data': 'string_goes_here'})
