# people/models.py

from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
# models.py
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission, User


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('staff', 'Staff'),
        ('visitor', 'Visitor'),
        ('researcher', 'Researcher'),
        ('speaker', 'Speaker'),
        ('writer', 'Writer'),
        ('partner', 'Partner'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    # Google OAuth fields
    google_token = models.TextField(blank=True, null=True)
    google_refresh_token = models.TextField(blank=True, null=True)
    google_token_expiry = models.DateTimeField(blank=True, null=True)

    # Add related_name to resolve clashes
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

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'people'

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
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()


    def __str__(self):
        return f"{self.person} - {self.position}"

class Speaker(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    bio = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    areas_of_expertise = models.CharField(
        max_length=255)  # Consider using a separate model for a many-to-many relationship
    speaking_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.person} - Speaker"

class Writer(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    genre = models.CharField(max_length=100)
    publications = models.TextField()

    def __str__(self):
        return f"{self.person} - Writer"

class PhotoBackup(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_photos = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    photos_limit = models.IntegerField(default=50, help_text=_("Number of photos to backup (0 for unlimited)"))

    def __str__(self):
        return f"Backup {self.id} - {self.user.email} - {self.status}"

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