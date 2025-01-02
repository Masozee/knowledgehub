from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from app.people.models import Person, CustomUser
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import uuid
from app.config.models import UserStampedModel
from app.project.models import Project


class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.name


class Event(UserStampedModel):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True)
    organizer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='events_organized'  # Changed from organized_events
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    venue_name = models.CharField(max_length=200)
    address = models.TextField()
    register = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    featured_image = models.ImageField(upload_to='events/images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    max_capacity = models.PositiveIntegerField(help_text="Maximum number of attendees")
    current_capacity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def is_full(self):
        return self.current_capacity >= self.max_capacity


class Speaker(models.Model):
    SPEAKER_TYPES = (
        ('keynote', 'Keynote Speaker'),
        ('guest', 'Guest Speaker'),
        ('panelist', 'Panelist'),
        ('moderator', 'Moderator'),
    )

    # Changed related_name to avoid clash
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='event_speaker_roles'  # Added specific related_name
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_speakers'  # Changed from speakers
    )
    speaker_type = models.CharField(max_length=20, choices=SPEAKER_TYPES)

    presentation_title = models.CharField(max_length=200)
    presentation_description = models.TextField()
    speaking_slot_start = models.DateTimeField()
    speaking_slot_end = models.DateTimeField()

    order = models.PositiveIntegerField(default=0, help_text="Order of appearance")
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event', 'order', 'speaking_slot_start']
        unique_together = ['event', 'person', 'speaking_slot_start']

    def __str__(self):
        return f"{self.person.full_name} - {self.event.title}"


class SpeakerAttachment(models.Model):
    ATTACHMENT_TYPES = (
        ('presentation', 'Presentation'),
        ('handout', 'Handout'),
        ('supplementary', 'Supplementary Material'),
    )

    speaker = models.ForeignKey(
        Speaker,
        on_delete=models.CASCADE,
        related_name='speaker_attachments'  # Changed from attachments
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES)

    file = models.FileField(
        upload_to='events/speaker_attachments/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'ppt', 'pptx', 'doc', 'docx']
            )
        ]
    )

    is_public = models.BooleanField(
        default=False,
        help_text="If true, attachment will be visible to all attendees"
    )

    upload_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.speaker}"
