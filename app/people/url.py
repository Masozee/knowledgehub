from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    path('backup/', views.backup_photos, name='backup_photos'),
]