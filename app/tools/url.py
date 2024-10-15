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
]