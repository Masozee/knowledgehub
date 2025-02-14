from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    path('backup/', views.backup_photos, name='backup_photos'),
    path('person/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
]