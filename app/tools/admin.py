from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Conversation, Message, TextContent, CodeContent, ImageContent

class MessageInline(GenericTabularInline):
    model = Message
    extra = 0
    fields = ('is_user', 'ai_service', 'content_preview')
    readonly_fields = ('content_preview',)

    def content_preview(self, obj):
        content = obj.content_object
        if isinstance(content, TextContent):
            return content.text[:50] + '...' if len(content.text) > 50 else content.text
        elif isinstance(content, CodeContent):
            return f"Code ({content.language}): {content.code[:50]}..."
        elif isinstance(content, ImageContent):
            return format_html('<img src="{}" style="max-width:100px; max-height:100px;" />', content.image.url)
        return "Unknown content type"

    content_preview.short_description = 'Content Preview'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at', 'is_cleared', 'is_deleted', 'message_count')
    list_filter = ('user', 'created_at', 'updated_at', 'is_cleared', 'is_deleted')
    search_fields = ('title', 'user__username')
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'message_count')
    inlines = [MessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Number of Messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation_link', 'is_user', 'ai_service', 'timestamp', 'content_type', 'content_preview')
    list_filter = ('is_user', 'ai_service', 'timestamp')
    search_fields = ('conversation__title', 'ai_service')
    readonly_fields = ('conversation_link', 'content_preview')

    def conversation_link(self, obj):
        url = reverse('admin:tools_conversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">{}</a>', url, obj.conversation.title)
    conversation_link.short_description = 'Conversation'

    def content_preview(self, obj):
        content = obj.content_object
        if isinstance(content, TextContent):
            return content.text[:100] + '...' if len(content.text) > 100 else content.text
        elif isinstance(content, CodeContent):
            return f"Code ({content.language}): {content.code[:100]}..."
        elif isinstance(content, ImageContent):
            return format_html('<img src="{}" style="max-width:200px; max-height:200px;" />', content.image.url)
        return "Unknown content type"
    content_preview.short_description = 'Content Preview'

@admin.register(TextContent)
class TextContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview')
    search_fields = ('text',)

    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'

@admin.register(CodeContent)
class CodeContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'language', 'code_preview')
    list_filter = ('language',)
    search_fields = ('code',)

    def code_preview(self, obj):
        return obj.code[:100] + '...' if len(obj.code) > 100 else obj.code
    code_preview.short_description = 'Code Preview'

@admin.register(ImageContent)
class ImageContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'image_preview')
    search_fields = ('caption',)

    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-width:100px; max-height:100px;" />', obj.image.url)
    image_preview.short_description = 'Image Preview'