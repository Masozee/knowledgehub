# urls.py
from django.urls import path
from . import views

app_name = 'project'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<uuid:uuid>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('complete/<uuid:uuid>/', views.mark_project_complete, name='complete'),
]
