from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from datetime import datetime, timedelta
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from app.project.mixins import AuditModelMixin
from app.people.models import Person


class PublicationCategory(AuditModelMixin, models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, editable=False)
    background = models.ImageField(
        upload_to='pub_category/',
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Publication Category")
        verbose_name_plural = _("Publication Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class PublicationAuthor(models.Model):
    """Simple model to manage publication authors with order"""
    publication = models.ForeignKey('Publication', on_delete=models.CASCADE)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    is_corresponding = models.BooleanField(
        default=False,
        help_text=_("Marks this author as a corresponding author")
    )
    affiliation = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ['publication', 'author']

    def __str__(self):
        return f"{self.author} - {self.publication}"


class PublicationTrackingEvent(models.Model):
    """Records individual tracking events for publications"""
    EVENT_TYPES = [
        ('download', 'Download'),
        ('view', 'View'),
    ]

    publication = models.ForeignKey('Publication', on_delete=models.CASCADE, related_name='tracking_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='publication_events'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['publication', 'event_type', 'timestamp']),
        ]

    @classmethod
    def get_aggregated_stats(cls, publication, event_type, start_date, end_date):
        return cls.objects.filter(
            publication=publication,
            event_type=event_type,
            timestamp__date__range=(start_date, end_date)
        ).count()


class PublicationStats(models.Model):
    """Stores pre-calculated statistics for publications"""
    publication = models.OneToOneField('Publication', on_delete=models.CASCADE, related_name='stats')

    # Daily stats
    daily_views = models.PositiveIntegerField(default=0)
    daily_downloads = models.PositiveIntegerField(default=0)
    last_daily_update = models.DateTimeField(null=True)

    # Weekly stats
    weekly_views = models.PositiveIntegerField(default=0)
    weekly_downloads = models.PositiveIntegerField(default=0)
    last_weekly_update = models.DateTimeField(null=True)

    # Monthly stats
    monthly_views = models.PositiveIntegerField(default=0)
    monthly_downloads = models.PositiveIntegerField(default=0)
    last_monthly_update = models.DateTimeField(null=True)

    def update_stats(self):
        now = timezone.now()
        today = now.date()

        # Update daily stats
        self.daily_views = PublicationTrackingEvent.get_aggregated_stats(
            self.publication, 'view', today, today)
        self.daily_downloads = PublicationTrackingEvent.get_aggregated_stats(
            self.publication, 'download', today, today)
        self.last_daily_update = now

        # Update weekly stats
        week_start = today - timedelta(days=today.weekday())
        self.weekly_views = PublicationTrackingEvent.get_aggregated_stats(
            self.publication, 'view', week_start, today)
        self.weekly_downloads = PublicationTrackingEvent.get_aggregated_stats(
            self.publication, 'download', week_start, today)
        self.last_weekly_update = now

        # Monthly stats
        month_start = today.replace(day=1)
        self.monthly_views = PublicationTrackingEvent.get_aggregated_stats(
            self.publication, 'view', month_start, today)
        self.monthly_downloads = PublicationTrackingEvent.get_aggregated_stats(
            self.publication, 'download', month_start, today)
        self.last_monthly_update = now

        self.save()


class Publication(AuditModelMixin, models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, editable=False)
    date_publish = models.DateField(blank=True, null=True)

    # Project connection
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='publications'
    )

    # Authors and Contributors
    authors = models.ManyToManyField(
        'people.Person',
        through='PublicationAuthor',
        related_name='authored_publications'
    )
    editor = models.ManyToManyField(
        'people.Person',
        blank=True,
        related_name='edited_publications'
    )
    partners = models.ManyToManyField(
        'people.Person',
        blank=True,
        related_name='partnered_publications'
    )

    # Classification
    category = models.ForeignKey(
        PublicationCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='publications'
    )
    topic = models.ManyToManyField('config.Option', blank=True)
    tags = TaggableManager(blank=True)

    # Content and Files
    description = RichTextField()
    image = models.ImageField(upload_to='publication/')
    image_credit = models.TextField(blank=True, null=True)
    cover = models.ImageField(
        upload_to='publication/cover/',
        blank=True,
        null=True
    )
    file = models.FileField(
        upload_to='publication/documents/',
        blank=True
    )

    # Status and Visibility
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    publish = models.BooleanField(default=False)
    highlight = models.BooleanField(default=False)

    # Tracking
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='added_publications'
    )
    viewed = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Publication")
        verbose_name_plural = _("Publications")
        ordering = ['-date_publish', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def current_stats(self):
        """Returns the current statistics for this publication"""
        stats, created = PublicationStats.objects.get_or_create(publication=self)
        return stats

    def record_view(self, user=None, ip_address=None, user_agent=None):
        """Record a view event for this publication"""
        event = PublicationTrackingEvent.objects.create(
            publication=self,
            event_type='view',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.viewed += 1
        self.save(update_fields=['viewed'])
        return event

    def record_download(self, user=None, ip_address=None, user_agent=None):
        """Record a download event for this publication"""
        event = PublicationTrackingEvent.objects.create(
            publication=self,
            event_type='download',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.download_count += 1
        self.save(update_fields=['download_count'])
        return event

    def get_author_list(self):
        """Returns a list of author names ordered by their position"""
        return [
            str(author.author)
            for author in self.publicationauthor_set.all().order_by('order')
        ]

    @property
    def author_list(self):
        """Property to easily access formatted author list"""
        authors = self.get_author_list()
        if not authors:
            return "-"
        return ", ".join(authors)

    @classmethod
    def get_topic_stats(cls):
        """Returns topic statistics including publication count, total views and downloads"""
        from django.db.models import Count, Sum

        return cls.objects.values(
            'topic__name',
            'topic__id'
        ).annotate(
            publication_count=Count('id'),
            total_views=Sum('viewed'),
            total_downloads=Sum('download_count')
        ).filter(
            status='published',
            publish=True
        ).order_by('-publication_count')

    @classmethod
    def get_tag_stats(cls):
        """Returns tag statistics including publication count, total views and downloads"""
        from django.db.models import Count, Sum
        from django.contrib.contenttypes.models import ContentType
        from taggit.models import Tag

        # Get all published publications
        published_pubs = cls.objects.filter(status='published', publish=True)

        # Get tags and their publication counts
        tags_data = Tag.objects.filter(
            taggit_taggeditem_items__content_type__model='publication',
            taggit_taggeditem_items__object_id__in=published_pubs.values_list('id', flat=True)
        ).annotate(
            publication_count=Count('taggit_taggeditem_items'),
        ).values('id', 'name', 'publication_count')

        # For each tag, calculate total views and downloads
        tags_stats = []
        for tag_data in tags_data:
            tag_publications = published_pubs.filter(tags__id=tag_data['id'])
            total_views = tag_publications.aggregate(Sum('viewed'))['viewed__sum'] or 0
            total_downloads = tag_publications.aggregate(Sum('download_count'))['download_count__sum'] or 0

            tags_stats.append({
                'tag__id': tag_data['id'],
                'tag__name': tag_data['name'],
                'publication_count': tag_data['publication_count'],
                'total_views': total_views,
                'total_downloads': total_downloads
            })

        # Sort by publication count
        return sorted(tags_stats, key=lambda x: x['publication_count'], reverse=True)