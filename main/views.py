from django.shortcuts import render
from django.http import HttpResponse
from main._01_backend import CryptoCharts

# Create your views here.

def landing_page(request):
    return render(request, "home.html", {})

def return_graphs_code(request):
    return HttpResponse(CryptoCharts().return_final_html())
