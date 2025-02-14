# people/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
# models.py
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission, User, BaseUserManager
from app.config.models import *

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'staff')  # Default type for superuser
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('staff', 'Staff'),
        ('visitor', 'Visitor'),
        ('researcher', 'Researcher'),
        ('speaker', 'Speaker'),
        ('writer', 'Writer'),
        ('partner', 'Partner'),
    )

    # Make email the main identifier
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)

    # Your existing fields
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    # OAuth fields (consolidated)
    oauth_provider = models.CharField(max_length=30, blank=True, null=True)  # 'google' or 'microsoft'
    oauth_token = models.TextField(blank=True, null=True)
    oauth_refresh_token = models.TextField(blank=True, null=True)
    oauth_token_expiry = models.DateTimeField(blank=True, null=True)

    # Email verification field
    is_email_verified = models.BooleanField(default=False)

    # Groups and Permissions (keep your existing related_names)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']  # Required during createsuperuser

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        app_label = 'people'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        # Ensure user_type is set
        if not self.user_type and not self.is_superuser:
            self.user_type = 'visitor'  # Default type for regular users
        super().save(*args, **kwargs)

    def get_avatar_color(self):
        colors = ['primary', 'success', 'warning', 'purple', 'danger', 'info', 'dark']
        return colors[hash(self.email) % len(colors)]

    def get_initials(self):
        """Get user's initials from full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.last_name:
            return self.last_name[0].upper()
        return self.username[0].upper() if self.username else 'U'

class Organization(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to='logo', blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Person(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='people/%Y/%m/%d/', null=True, blank=True)
    organization = models.ManyToManyField(
        Organization, blank=True, related_name='people', verbose_name='organization'
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    extension = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        """Returns the person's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_avatar_color(self):
        colors = ['primary', 'success', 'warning', 'purple', 'danger', 'info', 'dark']
        return colors[hash(self.email) % len(colors)]

    def get_initials(self):
        return ''.join(n[0].upper() for n in self.get_full_name().split()[:2])

class Relationship(models.Model):
    RELATIONSHIP_CHOICES = (
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships')
    related_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='reverse_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    kontak_darurat = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.person} is {self.relationship_type} of {self.related_person}"

class Staff(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(Option, limit_choices_to={'category': 5},on_delete=models.CASCADE)
    department = models.ForeignKey(Option, limit_choices_to={'category': 6},on_delete=models.CASCADE, related_name='departments')
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.person} - {self.position}"

class PhotoBackup(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_photos = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    photos_limit = models.IntegerField(default=0)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='initiated_backups'
    )

    class Meta:
        ordering = ['-created_at']

class Photo(models.Model):
    backup = models.ForeignKey(PhotoBackup, on_delete=models.CASCADE, related_name='photos')
    google_photo_id = models.CharField(max_length=500)  # Increased from 255
    filename = models.CharField(max_length=500)  # Increased from 255
    original_url = models.TextField()  # Changed from URLField to TextField
    mime_type = models.CharField(max_length=100)
    created_time = models.DateTimeField(null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    photo_file = models.FileField(upload_to='photo_backups/%Y/%m/%d/')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['backup', 'google_photo_id']

    def __str__(self):
        return f"{self.filename} - {self.backup.user.email}"