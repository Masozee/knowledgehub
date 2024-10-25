# urls.py
from django.urls import path
from . import views

app_name = 'project'

urlpatterns = [
    path('',
         views.ProjectListView.as_view(),
         name='project_list'
         ),
    path('<uuid:uuid>/',
         views.ProjectDetailView.as_view(),
         name='project_detail'
         ),
    path('detail/progress/', views.progress, name='detail-progress'),
]
