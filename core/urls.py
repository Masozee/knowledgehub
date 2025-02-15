# urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import LogoutView
from app.people import views as people_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('photo-backup/', people_views.admin_backup_photos, name='admin_photo_backup'),
    path('accounts/', include('allauth.urls')),  # This handles all auth URLs
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include('app.web.url')),
    path('tools/', include('app.tools.url')),
    path('project/', include('app.project.url')),
    path('publications/', include('app.publications.url')),
    path('events/', include('app.events.url')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('people/', include('app.people.url', namespace='photos_backup')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)