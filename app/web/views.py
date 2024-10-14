# views.py
from django.shortcuts import render

def index(request):
    return render(request, 'dashboard/index.html')

def userHome(request):
    return render(request, 'dashboard/user/index.html')

def wiki(request):
    return render(request, 'dashboard/wiki/index.html')

def srm(request):
    return render(request, 'dashboard/srm/index.html')

def assetList(request):
    return render(request, 'dashboard/asset/index.html')

def chatAI(request):
    return render(request, 'dashboard/chat/index.html')