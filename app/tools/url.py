from django.urls import path
from app.tools import views

app_name = 'tools'

urlpatterns = [
    path('test-logging/', views.test_logging, name='test_logging'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('<int:conversation_id>/', views.chat_detail, name='chat_detail'),
    path('<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('<int:conversation_id>/clear/', views.clear_conversation, name='clear_conversation'),
]