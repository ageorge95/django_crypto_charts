from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from time import sleep
from main._01_backend import CryptoCharts

# Create your views here.

def landing_page(request):
    return render(request, "home.html", {})

def return_graphs_code(request):
    return HttpResponse(CryptoCharts().return_html_code())
