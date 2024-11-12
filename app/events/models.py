from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from app.people.models import Person, CustomUser
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import uuid


class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.name


class Event(models.Model):
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
    # Changed related_name to avoid clash
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

    featured_image = models.ImageField(upload_to='events/images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    max_capacity = models.PositiveIntegerField(help_text="Maximum number of attendees")
    current_capacity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class TicketType(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_ticket_types'  # Changed from ticket_types
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()

    sale_start_date = models.DateTimeField()
    sale_end_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event.title} - {self.name}"

    def is_available(self):
        now = timezone.now()
        return (
                self.is_active and
                self.remaining > 0 and
                self.sale_start_date <= now <= self.sale_end_date
        )


class Ticket(models.Model):
    TICKET_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
    )

    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='event_tickets'  # Changed from tickets
    )

    ticket_number = models.CharField(max_length=100, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='tickets/qr_codes/', blank=True, null=True)
    unique_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='pending')

    attendee_name = models.CharField(max_length=200)
    attendee_email = models.EmailField()

    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.ticket_number} - {self.attendee_name}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TIX-{self.ticket_type.event.id}-{str(uuid.uuid4())[:8].upper()}"

        if not self.qr_code:
            self.generate_qr_code()

        super().save(*args, **kwargs)

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr_data = {
            'ticket_id': str(self.unique_identifier),
            'ticket_number': self.ticket_number,
            'event': self.ticket_type.event.title,
            'type': self.ticket_type.name
        }

        qr.add_data(str(qr_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'ticket-qr-{self.ticket_number}.png'

        self.qr_code.save(filename, File(buffer), save=False)
        buffer.close()


class EventReview(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_reviews'  # Changed from reviews
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='event_reviews_given'  # Added specific related_name
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.event.title} - {self.rating} stars"