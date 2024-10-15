# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'dashboard/index.html')

@login_required
def userHome(request):
    return render(request, 'dashboard/user/index.html')

@login_required
def wiki(request):
    return render(request, 'dashboard/wiki/index.html')

@login_required
def srm(request):
    return render(request, 'dashboard/srm/index.html')

@login_required
def assetList(request):
    return render(request, 'dashboard/asset/index.html')

@login_required
def chatAI(request):
    return render(request, 'dashboard/chat/index.html')