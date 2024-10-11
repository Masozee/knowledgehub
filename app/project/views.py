from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'dashboard/project/index.html')

def detail(request):
    return render(request, 'dashboard/project/detail.html')

def progress(request):
    return render(request, 'dashboard/project/progress.html')