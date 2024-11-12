from django.urls import path
from app.tools import views

app_name = 'tools'

urlpatterns = [
    path('test-logging/', views.test_logging, name='test_logging'),
    path('chat/', views.chat_list, name='chatlist'),
    path('chat/new/', views.new_conversation, name='new_conversation'),
    path('chat/<uuid:conversation_uuid>/', views.chat_detail, name='chat_detail'),
    path('chat/<uuid:conversation_uuid>/send/', views.send_message, name='send_message'),
    path('chat/<uuid:conversation_uuid>/delete/', views.delete_conversation, name='delete_conversation'),
    path('chat/<uuid:conversation_uuid>/clear/', views.clear_conversation, name='clear_conversation'),

    #notetaking
    path('videos/upload/', views.video_upload, name='video_upload'),
    # urls.py (likely configuration)
    path('videos/notes/<uuid:note_id>/', views.video_notes, name='video_notes'),
    path('videos/library/', views.video_library, name='video_library'),
    path('videos/status/<uuid:note_id>/', views.video_processing_status, name='video_processing_status'),
]