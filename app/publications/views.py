from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'dashboard/publications/detail.html')

def detail(request):
    return render(request, 'dashboard/publications/detail.html')