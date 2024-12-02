from django.contrib import contenttypes
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from app.config.models import *  # Import Category from app_config
from django.core.exceptions import ValidationError


class BaseDocument(UserStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Main content using WYSIWYG editor")

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-uploaded_at']


class SOP(BaseDocument):
    department = models.CharField(max_length=100)
    sop_number = models.CharField(max_length=50, unique=True)
    effective_date = models.DateField()
    review_date = models.DateField()
    version = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('approved', 'Approved'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    featured_image = models.ImageField(
        upload_to='sop_images/%Y/%m/%d/',
        null=True,
        blank=True
    )
    attachments = GenericRelation(Attachment)

    class Meta:
        verbose_name = "Standard Operating Procedure"
        verbose_name_plural = "Standard Operating Procedures"

    def __str__(self):
        return f"{self.sop_number} - {self.title}"


class News(BaseDocument):
    excerpt = models.TextField(max_length=500, help_text="Brief summary of the news")
    publish_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    featured_image = models.ImageField(
        upload_to='news_images/%Y/%m/%d/',
        null=True,
        blank=True
    )
    categories = models.ManyToManyField(Category, related_name='news')  # Updated to use Category from app_config
    attachments = GenericRelation(Attachment)

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def __str__(self):
        return self.title


class Bulletin(BaseDocument):
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        default='low'
    )
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    featured_image = models.ImageField(
        upload_to='bulletin_images/%Y/%m/%d/',
        null=True,
        blank=True
    )
    attachments = GenericRelation(Attachment)

    def __str__(self):
        return f"{self.priority.upper()} - {self.title}"


class BaseHoliday(UserStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    is_recurring = models.BooleanField(
        default=False,
        help_text="If checked, this holiday will occur on the same date every year"
    )

    class Meta:
        abstract = True
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%d %B %Y')})"

    def clean(self):
        # Prevent duplicate dates for non-recurring holidays
        if not self.is_recurring:
            existing_holiday = self.__class__.objects.filter(
                date=self.date
            ).exclude(id=self.id)
            if existing_holiday.exists():
                raise ValidationError(f"A holiday already exists on {self.date}")


class PublicHoliday(BaseHoliday):
    holiday_type = models.CharField(
        max_length=50,
        choices=[
            ('national', 'National Holiday'),
            ('state', 'State Holiday'),
            ('religious', 'Religious Holiday'),
            ('other', 'Other')
        ],
        default='national'
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="Applicable state (if this is a state holiday)"
    )

    class Meta:
        verbose_name = "Public Holiday"
        verbose_name_plural = "Public Holidays"
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'holiday_type', 'state'],
                name='unique_public_holiday'
            )
        ]


class InternalHoliday(BaseHoliday):
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Leave blank if holiday applies to all departments"
    )
    applicable_to = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text="Select specific groups this holiday applies to"
    )
    notification_days = models.PositiveIntegerField(
        default=7,
        help_text="Days before holiday to send notification"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('cancelled', 'Cancelled')
        ],
        default='draft'
    )

    class Meta:
        verbose_name = "Internal Holiday"
        verbose_name_plural = "Internal Holidays"

    def is_upcoming(self):
        today = timezone.now().date()
        return self.date > today and self.status == 'approved'

    def days_until(self):
        today = timezone.now().date()
        return (self.date - today).days