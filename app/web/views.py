# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.people.models import *



@login_required(login_url='/accounts/login/')
def index(request):
    try:
        user = CustomUser.objects.get(email=request.user.email)
        context = {
            'user': user,
            'user_type': user.user_type,  # Since you have a user_type field
            'is_verified': user.is_email_verified,
        }
        return render(request, 'dashboard/index.html', context)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')

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