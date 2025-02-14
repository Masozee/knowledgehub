# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import *
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import truncatechars
from django.utils.safestring import mark_safe


@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'timestamp', 'database_type', 'status', 'file_size_formatted')
    list_filter = ('status', 'database_type', 'created_at')
    search_fields = ('file_name',)
    readonly_fields = ('timestamp', 'file_size', 'created_at')

    def file_size_formatted(self, obj):
        # Convert bytes to MB
        size_mb = obj.file_size / (1024 * 1024)
        return f"{size_mb:.2f} MB"

    file_size_formatted.short_description = 'File Size'


@admin.register(AnalyticsVisitorData)
class AnalyticsVisitorDataAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'source', 'device', 'browser', 'country', 'ip_address')
    list_filter = ('device', 'browser', 'os', 'country')
    search_fields = ('ip_address', 'source')
    date_hierarchy = 'timestamp'


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('content_preview', 'timestamp')
    fields = ('is_user', 'ai_service', 'content_preview', 'timestamp')

    def content_preview(self, obj):
        if obj.content_object:
            if isinstance(obj.content_object, TextContent):
                return obj.content_object.text[:100] + '...'
            elif isinstance(obj.content_object, CodeContent):
                return f"Code ({obj.content_object.language})"
            elif isinstance(obj.content_object, ImageContent):
                return "Image"
        return "No content"

    content_preview.short_description = 'Content'

'''
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'message_count', 'view_conversation')
    list_filter = ('created_at', 'user', 'is_cleared', 'is_deleted')
    search_fields = ('title', 'user__username')
    inlines = [MessageInline]
    readonly_fields = ('uuid', 'created_at', 'updated_at')

    def message_count(self, obj):
        return obj.messages.count()

    message_count.short_description = 'Messages'

    def view_conversation(self, obj):
        url = reverse('tools:chat_detail', kwargs={'conversation_uuid': obj.uuid})
        return format_html('<a href="{}" target="_blank">View Chat</a>', url)

    view_conversation.short_description = 'View'

'''
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation_title', 'message_type', 'is_user', 'ai_service', 'timestamp')
    list_filter = ('is_user', 'ai_service', 'timestamp')
    search_fields = ('conversation__title', 'content_type__model')
    readonly_fields = ('id', 'timestamp')

    def conversation_title(self, obj):
        return obj.conversation.title

    conversation_title.short_description = 'Conversation'

    def message_type(self, obj):
        return obj.content_type.model.capitalize()

    message_type.short_description = 'Type'


@admin.register(TextContent)
class TextContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview')
    search_fields = ('text',)
    readonly_fields = ('id',)

    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text

    text_preview.short_description = 'Text'


@admin.register(CodeContent)
class CodeContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'language', 'code_preview')
    list_filter = ('language',)
    search_fields = ('code',)
    readonly_fields = ('id',)

    def code_preview(self, obj):
        return obj.code[:100] + '...' if len(obj.code) > 100 else obj.code

    code_preview.short_description = 'Code'


@admin.register(ImageContent)
class ImageContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'caption')
    search_fields = ('caption',)
    readonly_fields = ('id',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "No image"

    image_preview.short_description = 'Image'


@admin.register(VideoContent)
class VideoContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_formatted', 'source_type', 'created_at', 'transcript_links', 'video_preview')
    list_filter = (
        'created_at',
        ('source_url', admin.EmptyFieldListFilter),  # Fixed filter for source_url
    )
    search_fields = ('title', 'source_url')
    readonly_fields = ('duration_formatted', 'transcript_preview', 'video_preview', 'download_links')
    fieldsets = (
        ('Video Information', {
            'fields': ('title', 'source_url', 'duration_formatted', 'video_file', 'video_preview')
        }),
        ('Transcript Files', {
            'fields': ('transcript_preview', 'download_links'),
            'classes': ('collapse',)
        }),
    )

    def duration_formatted(self, obj):
        if not obj.duration:
            return '-'
        hours = int(obj.duration // 3600)
        minutes = int((obj.duration % 3600) // 60)
        seconds = int(obj.duration % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    duration_formatted.short_description = 'Duration'

    def source_type(self, obj):
        return 'YouTube' if obj.source_url else 'Local Upload'

    source_type.short_description = 'Source'
    source_type.admin_order_field = 'source_url'  # Enable sorting

    def transcript_links(self, obj):
        links = []
        if obj.transcript_txt_path:
            links.append(f'<a href="{obj.transcript_txt_path}" target="_blank">TXT</a>')
        if obj.transcript_srt_path:
            links.append(f'<a href="{obj.transcript_srt_path}" target="_blank">SRT</a>')
        if obj.transcript_vtt_path:
            links.append(f'<a href="{obj.transcript_vtt_path}" target="_blank">VTT</a>')
        if obj.transcript_json_path:
            links.append(f'<a href="{obj.transcript_json_path}" target="_blank">JSON</a>')

        return format_html(' | '.join(links)) if links else '-'

    transcript_links.short_description = 'Transcripts'

    def video_preview(self, obj):
        if obj.video_file:
            return format_html(
                '<video width="320" height="240" controls>'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>',
                obj.video_file.url
            )
        return '-'

    video_preview.short_description = 'Video Preview'

    def transcript_preview(self, obj):
        try:
            if obj.transcript_txt_path and os.path.exists(obj.transcript_txt_path):
                with open(obj.transcript_txt_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # First 1000 characters
                    return format_html(
                        '<div style="max-height: 300px; overflow-y: auto; '
                        'font-family: monospace; white-space: pre-wrap;">{}</div>',
                        content + ('...' if len(content) == 1000 else '')
                    )
        except Exception as e:
            return f"Error loading transcript: {str(e)}"
        return "No transcript available"

    transcript_preview.short_description = 'Transcript Preview'

    def download_links(self, obj):
        links = []
        formats = {
            'TXT': obj.transcript_txt_path,
            'SRT': obj.transcript_srt_path,
            'VTT': obj.transcript_vtt_path,
            'JSON': obj.transcript_json_path
        }

        for format_name, path in formats.items():
            if path and os.path.exists(path):
                links.append(
                    f'<a href="{path}" class="button" '
                    f'style="margin: 2px 5px;">'
                    f'Download {format_name}</a>'
                )

        return format_html('<div style="display: flex; flex-wrap: wrap;">{}</div>',
                           format_html(''.join(links))) if links else "No downloads available"

    download_links.short_description = 'Download Transcripts'

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly if this is an existing object"""
        if obj:  # This is an edit
            return self.readonly_fields + ('source_url',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """Custom save method to handle any additional processing"""
        if not change:  # This is a new object
            obj.duration = obj.duration or 0  # Ensure duration has a default value
        super().save_model(request, obj, form, change)


class VideoNoteInline(admin.StackedInline):
    model = VideoNote
    extra = 0
    readonly_fields = ('transcript', 'summary', 'key_points')
    can_delete = False
    max_num = 1
    classes = ('collapse',)


@admin.register(VideoNote)
class VideoNoteAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'created_at', 'has_transcript', 'has_summary', 'key_points_count')
    list_filter = ('created_at',)
    search_fields = ('video__title', 'transcript', 'summary')
    readonly_fields = ('video_link', 'transcript_preview', 'analysis_preview')
    fieldsets = (
        ('Video Information', {
            'fields': ('video', 'video_link', 'conversation')
        }),
        ('Content', {
            'fields': ('transcript_preview', 'analysis_preview'),
            'classes': ('collapse',)
        }),
    )

    def video_title(self, obj):
        return obj.video.title if obj.video else '-'

    video_title.short_description = 'Video'
    video_title.admin_order_field = 'video__title'

    def has_transcript(self, obj):
        return bool(obj.transcript)

    has_transcript.boolean = True
    has_transcript.short_description = 'Has Transcript'

    def has_summary(self, obj):
        return bool(obj.summary)

    has_summary.boolean = True
    has_summary.short_description = 'Has Summary'

    def key_points_count(self, obj):
        return len(obj.key_points) if obj.key_points else 0

    key_points_count.short_description = 'Key Points'

    def video_link(self, obj):
        if obj.video:
            url = reverse('admin:tools_videocontent_change', args=[obj.video.id])
            return format_html('<a href="{}">{}</a>', url, obj.video.title)
        return '-'

    video_link.short_description = 'Video Link'

    def transcript_preview(self, obj):
        if obj.transcript:
            return format_html(
                '<div style="max-height: 300px; overflow-y: auto; '
                'font-family: monospace; white-space: pre-wrap;">{}</div>',
                truncatechars(obj.transcript, 1000)
            )
        return "No transcript available"

    transcript_preview.short_description = 'Transcript Preview'

    def analysis_preview(self, obj):
        content = []
        if obj.summary:
            content.append(f"<strong>Summary:</strong><br>{obj.summary}<br><br>")
        if obj.key_points:
            points = "<br>".join(f"• {point}" for point in obj.key_points)
            content.append(f"<strong>Key Points:</strong><br>{points}")

        return format_html(
            '<div style="max-height: 300px; overflow-y: auto;">{}</div>',
            mark_safe(''.join(content)) if content else "No analysis available"
        )

    analysis_preview.short_description = 'Analysis Preview'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'message_count')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'user__username')
    readonly_fields = ('message_preview',)

    def message_count(self, obj):
        return obj.message_set.count()

    message_count.short_description = 'Messages'

    def message_preview(self, obj):
        messages = obj.message_set.select_related('content_type')[:5]
        content = []
        for msg in messages:
            if msg.content_type and msg.object_id:
                try:
                    text_content = msg.content_object.text if hasattr(msg.content_object, 'text') else str(
                        msg.content_object)
                    content.append(f"{'User' if msg.is_user else 'System'}: {truncatechars(text_content, 100)}")
                except:
                    continue

        return format_html(
            '<div style="max-height: 300px; overflow-y: auto;">{}</div>',
            '<br>'.join(content) + ('<br>...' if obj.message_set.count() > 5 else '')
        )

    message_preview.short_description = 'Recent Messages'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)

'''
class SupportRequestVersionInline(admin.TabularInline):
    model = SupportRequestVersion
    extra = 0
    readonly_fields = ['version', 'title', 'description', 'request_type', 'created_at', 'created_by']
    can_delete = False
    ordering = ['-version']
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False


class SupportAssistanceInline(admin.TabularInline):
    model = SupportAssistance
    extra = 1
    autocomplete_fields = ['staff_member']
    fields = ['staff_member', 'notes', 'is_active', 'requested_by']


class SupportCommentInline(admin.TabularInline):
    model = SupportComment
    extra = 0
    fields = ['author', 'content', 'internal_note', 'attachment']
    readonly_fields = ['created_at']


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'request_type',
        'priority',
        'status',
        'requested_by',
        'assigned_to',
        'due_date',
        'is_overdue_status',
        'version',
        'created_at'
    ]
    list_filter = [
        'status',
        'priority',
        'request_type',
        ('assigned_to', admin.RelatedOnlyFieldListFilter),
        'created_at',
    ]
    search_fields = [
        'title',
        'description',
        'requested_by__email',
        'assigned_to__person__first_name',
        'assigned_to__person__last_name'
    ]
    readonly_fields = ['version', 'created_at', 'updated_at', 'created_by', 'updated_by']
    autocomplete_fields = ['requested_by', 'assigned_to', 'project']
    date_hierarchy = 'created_at'
    inlines = [SupportRequestVersionInline, SupportAssistanceInline, SupportCommentInline]

    fieldsets = (
        ('Request Information', {
            'fields': (
                'title',
                'description',
                'request_type',
                'priority',
                'status',
                'project'
            )
        }),
        ('Assignment', {
            'fields': (
                'requested_by',
                'assigned_to',
                'due_date'
            )
        }),
        ('Resolution', {
            'fields': (
                'resolution_notes',
                'resolved_at'
            ),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': (
                'version',
                'created_by',
                'created_at',
                'updated_by',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )

    def is_overdue_status(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="color: red;">⚠️ Overdue</span>'
            )
        return format_html(
            '<span style="color: green;">✓ On track</span>'
        )

    is_overdue_status.short_description = 'Status'

    actions = ['mark_resolved', 'mark_in_progress', 'mark_on_hold']

    @admin.action(description="Mark selected requests as resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(
            status='resolved',
            resolved_at=timezone.now(),
            updated_by=request.user
        )

    @admin.action(description="Mark selected requests as in progress")
    def mark_in_progress(self, request, queryset):
        queryset.update(
            status='in_progress',
            updated_by=request.user
        )

    @admin.action(description="Mark selected requests as on hold")
    def mark_on_hold(self, request, queryset):
        queryset.update(
            status='on_hold',
            updated_by=request.user
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'requested_by',
            'assigned_to',
            'project'
        )


@admin.register(SupportComment)
class SupportCommentAdmin(admin.ModelAdmin):
    list_display = [
        'support_request_link',
        'author',
        'content_preview',
        'is_reply',
        'internal_note',
        'has_attachment',
        'created_at'
    ]
    list_filter = [
        'internal_note',
        'created_at',
        ('author', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = [
        'content',
        'author__email',
        'support_request__title'
    ]
    autocomplete_fields = ['support_request', 'author', 'parent']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def support_request_link(self, obj):
        url = reverse('admin:support_supportrequest_change', args=[obj.support_request.id])
        return format_html('<a href="{}">{}</a>', url, obj.support_request.title)

    support_request_link.short_description = 'Support Request'

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content

    content_preview.short_description = 'Content'

    def has_attachment(self, obj):
        return bool(obj.attachment)

    has_attachment.boolean = True
    has_attachment.short_description = 'Attachment'


@admin.register(SupportAssignment)
class SupportAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'support_request_link',
        'staff_member',
        'assigned_by',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'created_at',
        ('staff_member', admin.RelatedOnlyFieldListFilter),
        ('assigned_by', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = [
        'support_request__title',
        'staff_member__person__first_name',
        'staff_member__person__last_name',
        'assigned_by__email'
    ]
    autocomplete_fields = ['support_request', 'staff_member', 'assigned_by']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def support_request_link(self, obj):
        url = reverse('admin:support_supportrequest_change', args=[obj.support_request.id])
        return format_html('<a href="{}">{}</a>', url, obj.support_request.title)

    support_request_link.short_description = 'Support Request'


@admin.register(SupportAssistance)
class SupportAssistanceAdmin(admin.ModelAdmin):
    list_display = [
        'support_request_link',
        'staff_member',
        'requested_by',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'created_at',
        ('staff_member', admin.RelatedOnlyFieldListFilter),
        ('requested_by', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = [
        'support_request__title',
        'staff_member__person__first_name',
        'staff_member__person__last_name',
        'requested_by__email'
    ]
    autocomplete_fields = ['support_request', 'staff_member', 'requested_by']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def support_request_link(self, obj):
        url = reverse('admin:support_supportrequest_change', args=[obj.support_request.id])
        return format_html('<a href="{}">{}</a>', url, obj.support_request.title)

    support_request_link.short_description = 'Support Request'

'''