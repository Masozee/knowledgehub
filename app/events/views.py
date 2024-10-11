from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'dashboard/events/index.html')

def detail(request):
    return render(request, 'dashboard/events/detail.html')