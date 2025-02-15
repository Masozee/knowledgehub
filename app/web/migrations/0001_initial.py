# Generated by Django 5.1.1 on 2024-12-28 16:15

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("config", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to="attachments/%Y/%m/%d/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="Bulletin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "content",
                    models.TextField(help_text="Main content using WYSIWYG editor"),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("urgent", "Urgent"),
                        ],
                        default="low",
                        max_length=20,
                    ),
                ),
                ("expiry_date", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "featured_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="bulletin_images/%Y/%m/%d/"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="InternalHoliday",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("date", models.DateField()),
                (
                    "is_recurring",
                    models.BooleanField(
                        default=False,
                        help_text="If checked, this holiday will occur on the same date every year",
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        blank=True,
                        help_text="Leave blank if holiday applies to all departments",
                        max_length=100,
                    ),
                ),
                (
                    "notification_days",
                    models.PositiveIntegerField(
                        default=7, help_text="Days before holiday to send notification"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("approved", "Approved"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                (
                    "applicable_to",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Select specific groups this holiday applies to",
                        to="auth.group",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Internal Holiday",
                "verbose_name_plural": "Internal Holidays",
            },
        ),
        migrations.CreateModel(
            name="News",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "content",
                    models.TextField(help_text="Main content using WYSIWYG editor"),
                ),
                (
                    "excerpt",
                    models.TextField(
                        help_text="Brief summary of the news", max_length=500
                    ),
                ),
                (
                    "publish_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("is_published", models.BooleanField(default=False)),
                (
                    "featured_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="news_images/%Y/%m/%d/"
                    ),
                ),
                (
                    "categories",
                    models.ManyToManyField(related_name="news", to="config.category"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "News Article",
                "verbose_name_plural": "News Articles",
            },
        ),
        migrations.CreateModel(
            name="SOP",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "content",
                    models.TextField(help_text="Main content using WYSIWYG editor"),
                ),
                ("department", models.CharField(max_length=100)),
                ("sop_number", models.CharField(max_length=50, unique=True)),
                ("effective_date", models.DateField()),
                ("review_date", models.DateField()),
                ("version", models.CharField(max_length=20)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("review", "Under Review"),
                            ("approved", "Approved"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                (
                    "featured_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="sop_images/%Y/%m/%d/"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Standard Operating Procedure",
                "verbose_name_plural": "Standard Operating Procedures",
            },
        ),
        migrations.CreateModel(
            name="PublicHoliday",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("date", models.DateField()),
                (
                    "is_recurring",
                    models.BooleanField(
                        default=False,
                        help_text="If checked, this holiday will occur on the same date every year",
                    ),
                ),
                (
                    "holiday_type",
                    models.CharField(
                        choices=[
                            ("national", "National Holiday"),
                            ("state", "State Holiday"),
                            ("religious", "Religious Holiday"),
                            ("other", "Other"),
                        ],
                        default="national",
                        max_length=50,
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        blank=True,
                        help_text="Applicable state (if this is a state holiday)",
                        max_length=100,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Public Holiday",
                "verbose_name_plural": "Public Holidays",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("date", "holiday_type", "state"),
                        name="unique_public_holiday",
                    )
                ],
            },
        ),
    ]
