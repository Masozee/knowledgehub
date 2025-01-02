# urls.py
from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.userHome, name='index-user'),
    path('wiki/', views.wiki, name='index-wiki'),
    path('srm/', views.srm, name='index-srm'),
    path('asset/', views.assetList, name='index-asset'),
    path('news/', views.assetList, name='index-news'),
    path('bulletins/', views.assetList, name='index-bulletins'),
    path('procedure/', views.assetList, name='index-sop'),
    path('calendar/', views.calendar, name='index-calendar'),
]
