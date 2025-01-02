from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.middleware import get_current_user
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages




class TimeStampedMixin(models.Model):
    """
    Abstract base class mixin that provides self-updating
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
        editable=False,
        help_text=_("Date and time when the record was created")
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
        editable=False,
        help_text=_("Date and time when the record was last updated")
    )

    class Meta:
        abstract = True


class UserStampedMixin(models.Model):
    """
    Abstract base class mixin that provides created_by and updated_by
    fields linked to User model.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Created by"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_%(class)s_created",
        help_text=_("User who created this record")
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Updated by"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_%(class)s_updated",
        help_text=_("User who last updated this record")
    )

    class Meta:
        abstract = True


class AuditModelMixin(TimeStampedMixin, UserStampedMixin):
    """
    Combines TimeStampedMixin and UserStampedMixin to provide
    complete audit trail functionality.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override save method to update user stamps automatically
        """
        user = kwargs.pop('user', None)
        skip_log = kwargs.pop('skip_log', False)

        # Get the current user from thread local storage if not explicitly provided
        current_user = user or getattr(self, '_current_user', None) or get_current_user()

        if current_user and not current_user.is_anonymous:
            if not self.pk:  # If creating new instance
                self.created_by = current_user
            self.updated_by = current_user

        # Store current_user for activity logging
        self._current_user = current_user

        # Call parent save
        super().save(*args, **kwargs)

        # Handle activity logging
        if not skip_log and not kwargs.get('skip_activity_log', False):
            try:
                from project.models import ActivityLog

                # Only log creation for new instances
                if not self.pk:
                    # Determine the related project
                    if hasattr(self, 'project_id') and self.project_id:
                        related_project = self.project
                    elif self._meta.model_name == 'project':
                        related_project = self
                    else:
                        related_project = None

                    if related_project and current_user:
                        ActivityLog.log_activity(
                            actor=current_user,
                            action_type='create',
                            content_object=self,
                            project=related_project,
                            description=f"Created new {self._meta.verbose_name}: {str(self)}"
                        )
            except ImportError:
                pass