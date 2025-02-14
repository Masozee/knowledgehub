import os
import uuid
import subprocess
from django.db import models, connection
from django.conf import settings
from django.core.exceptions import ValidationError
from decouple import config
from django.utils.text import slugify
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from app.project.mixins import AuditModelMixin
import yt_dlp
from pydub import AudioSegment
import tempfile

User = get_user_model()

class DatabaseBackup(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    database_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backup {self.file_name} created at {self.timestamp}"

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        super().delete(*args, **kwargs)

    def restore(self):
        db_name = config('DB_NAME')
        db_user = config('DB_USER')
        db_password = config('DB_PASSWORD')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')

        psql_path = self.find_psql()
        if not psql_path:
            raise ValidationError('Could not find psql.exe. Please ensure PostgreSQL is installed.')

        backup_file = self.file_name

        # Close the current database connection
        connection.close()

        # Wrap the psql_path in quotes to handle spaces
        psql_path = f'"{psql_path}"'

        # Terminate all connections to the database
        terminate_connections = f'{psql_path} -h {db_host} -p {db_port} -U {db_user} -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'{db_name}\' AND pid <> pg_backend_pid();"'

        # Truncate all tables in the database
        truncate_tables = f'{psql_path} -h {db_host} -p {db_port} -U {db_user} -d {db_name} -c "DO $$ DECLARE r RECORD; BEGIN FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP EXECUTE \'TRUNCATE TABLE \' || quote_ident(r.tablename) || \' CASCADE\'; END LOOP; END $$;"'

        # Restore command
        restore_command = f'{psql_path} -h {db_host} -p {db_port} -U {db_user} -d {db_name} -f "{backup_file}"'

        try:
            # Terminate connections
            self.run_command(terminate_connections, db_password)

            # Truncate all tables
            self.run_command(truncate_tables, db_password)

            # Restore from backup
            self.run_command(restore_command, db_password)

            # Run migrations
            from django.core.management import call_command
            call_command('migrate')

        except subprocess.CalledProcessError as e:
            error_message = f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.\n"
            if e.stdout:
                error_message += f"Stdout: {e.stdout}\n"
            if e.stderr:
                error_message += f"Stderr: {e.stderr}\n"
            raise ValidationError(f'An error occurred during the database restore process: {error_message}')

    def run_command(self, command, password):
        result = subprocess.run(command, shell=True, env={**os.environ, 'PGPASSWORD': password}, check=True,
                                capture_output=True, text=True)
        if result.stderr:
            raise ValidationError(f"Error executing command: {result.stderr}")
        return result

    def find_psql(self):
        common_dirs = [
            r'C:\Program Files\PostgreSQL',
            r'C:\Program Files (x86)\PostgreSQL',
        ]

        for base_dir in common_dirs:
            if os.path.exists(base_dir):
                versions = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
                versions.sort(reverse=True)
                for version in versions:
                    psql_path = os.path.join(base_dir, version, 'bin', 'psql.exe')
                    if os.path.exists(psql_path):
                        return psql_path
        return None

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.message}"

class AnalyticsVisitorData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=255)
    device = models.CharField(max_length=100)
    browser = models.CharField(max_length=100)
    os = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()

    class Meta:
        app_label = 'tools'

class Conversation(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    is_cleared = models.BooleanField(default=False, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.title:
            current_time = self.created_at or timezone.now()
            self.title = f"Conversation {current_time.strftime('%Y-%m-%d %H:%M')}"

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def clear_chat(self):
        self.messages.all().delete()
        self.is_cleared = True
        self.save()

    def delete_conversation(self):
        self.is_deleted = True
        self.save()

    @property
    def full_path(self):
        return reverse('tools:chat_detail', kwargs={'conversation_uuid': self.uuid})

    def update_title(self, new_title):
        self.title = new_title
        self.save()

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    AI_SERVICE_CHOICES = [
        ('claude', 'Claude'),
        ('openai', 'OpenAI'),
        ('perplexity', 'Perplexity'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField()
    ai_service = models.CharField(max_length=20, choices=AI_SERVICE_CHOICES, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)

    # Use GenericForeignKey to link to different content types
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'} message in {self.conversation.title}"

    class Meta:
        ordering = ['timestamp']

class TextContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()

class CodeContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.TextField()
    language = models.CharField(max_length=50)

class ImageContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='ai_images/')
    caption = models.CharField(max_length=255, blank=True)

class VideoContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    source_url = models.URLField(null=True, blank=True)
    video_file = models.FileField(
        upload_to='videos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov'])]
    )
    duration = models.IntegerField(null=True, blank=True)  # Duration in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    messages = GenericRelation('Message')
    transcript_txt_path = models.CharField(max_length=255, blank=True)
    transcript_json_path = models.CharField(max_length=255, blank=True)
    transcript_srt_path = models.CharField(max_length=255, blank=True)
    transcript_vtt_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

class VideoNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.OneToOneField(VideoContent, on_delete=models.CASCADE)
    transcript = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list)
    conclusion = models.TextField(blank=True, null=True)  # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.video.title}"

    class Meta:
        ordering = ['-created_at']




class SupportRequest(AuditModelMixin, models.Model):
    """
    Model for handling support requests from users
    """
    REQUEST_TYPE_CHOICES = (
        ('technical', 'Technical Support'),
        ('access', 'Access Request'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('inquiry', 'General Inquiry'),
        ('data', 'Data Support'),
        ('assistance', 'Staff Assistance'),
        ('other', 'Other'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )

    # Basic Fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Timestamps and Tracking
    due_date = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)

    # Related Project (Optional)
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_requests'
    )

    # User Relations
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_support_requests'
    )
    assigned_to = models.ForeignKey(
        'people.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_support_requests'
    )

    # For assistance requests
    assistance_staff = models.ManyToManyField(
        'people.Staff',
        through='SupportAssistance',
        related_name='assisted_requests',
        blank=True
    )

    # Attachments
    attachments = models.FileField(
        upload_to='support_attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png', 'txt']
        )],
        null=True,
        blank=True
    )

    priority_changed_at = models.DateTimeField(null=True, blank=True)
    satisfaction_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    tags = models.ManyToManyField('SupportTag', blank=True)


    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = SupportRequest.objects.get(pk=self.pk)
            if old_instance.priority != self.priority:
                self.priority_changed_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['requested_by']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def get_absolute_url(self):
        return reverse('support:request_detail', kwargs={'pk': self.pk})

    def assign_to_staff(self, staff_member, assigned_by):
        """Assign request to staff member"""
        self.assigned_to = staff_member
        self.status = 'assigned'
        self._current_user = assigned_by
        self.save()

        # Create assignment record
        SupportAssignment.objects.create(
            support_request=self,
            staff_member=staff_member,
            assigned_by=assigned_by
        )

    def save(self, *args, **kwargs):
        # Handle versioning
        if self.pk:
            current = SupportRequest.objects.get(pk=self.pk)
            if (current.title != self.title or
                    current.description != self.description or
                    current.request_type != self.request_type):
                # Create version history
                SupportRequestVersion.objects.create(
                    support_request=self,
                    title=current.title,
                    description=current.description,
                    request_type=current.request_type,
                    version=self.version
                )
                self.version += 1

        super().save(*args, **kwargs)

    @property
    def is_resolved(self):
        return self.status in ['resolved', 'closed']

    @property
    def is_overdue(self):
        if self.due_date and not self.is_resolved:
            return timezone.now() > self.due_date
        return False

    def resolve(self, resolution_notes, resolved_by):
        """Mark request as resolved"""
        self.status = 'resolved'
        self.resolution_notes = resolution_notes
        self.resolved_at = timezone.now()
        self._current_user = resolved_by
        self.save()

class SupportTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#FF0000")

    def __str__(self):
        return self.name

class SupportRequestVersion(models.Model):
    """
    Model to track versions of support requests
    """
    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    request_type = models.CharField(max_length=20, choices=SupportRequest.REQUEST_TYPE_CHOICES)
    version = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-version']
        unique_together = ['support_request', 'version']

    def __str__(self):
        return f"{self.support_request.title} - v{self.version}"


class SupportAssignment(AuditModelMixin, models.Model):
    """
    Model to track support request assignments
    """
    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    staff_member = models.ForeignKey(
        'people.Staff',
        on_delete=models.CASCADE,
        related_name='support_assignments'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_support_requests'
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.support_request} assigned to {self.staff_member}"


class SupportAssistance(AuditModelMixin, models.Model):
    """
    Model to track additional staff members assisting with a request
    """
    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name='assistance_records'
    )
    staff_member = models.ForeignKey(
        'people.Staff',
        on_delete=models.CASCADE,
        related_name='assistance_records'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_assistance'
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['support_request', 'staff_member']

    def __str__(self):
        return f"{self.staff_member} assisting on {self.support_request}"


class SupportComment(AuditModelMixin, models.Model):
    """
    Model for comments and replies on support requests
    """
    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_comments'
    )
    content = models.TextField()
    internal_note = models.BooleanField(
        default=False,
        help_text="If checked, this comment is only visible to staff members"
    )
    # For threaded comments
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    attachment = models.FileField(
        upload_to='support_comments/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png', 'txt']
        )],
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.support_request}"

    @property
    def is_reply(self):
        return self.parent is not None

    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.all().order_by('created_at')