# urls.py
from django.urls import path
from .views import *

app_name = 'events'

urlpatterns = [
    path('', index.as_view(), name='event_list'),
    path('<slug:slug>/', detail.as_view(), name='event_detail'),
]
