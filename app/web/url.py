# urls.py
from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('dashboard/', views.index, name='index'),
    path('user/', views.userHome, name='index-user'),
    path('wiki/', views.wiki, name='index-wiki'),
]