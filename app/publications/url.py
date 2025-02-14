# urls.py
from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('list/', views.PublicationListView.as_view(), name='list'),
    path('topics/', views.PublicationTopicListView.as_view(), name='publication-topics'),
    path('tags/', views.PublicationTagListView.as_view(), name='publication-tags'),
    path('submissions/', views.PublicationSubmissionListView.as_view(), name='publication-submissions'),
    path('<slug:slug>/', views.PublicationDetailView.as_view(), name='publication-detail'),
    path('<slug:slug>/download/', views.PublicationDownloadView.as_view(), name='publication-download'),

]
