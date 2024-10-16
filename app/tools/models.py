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


class DatabaseBackup(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()

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
        return reverse('tools:chat_detail', kwargs={'conversation_uuid': str(self.uuid)})

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

