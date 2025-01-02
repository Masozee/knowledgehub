from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
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
    # Modified partners field to remove the problematic limit_choices_to
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