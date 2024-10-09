# config/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class UserStampedModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Created by"),
        related_name="%(app_label)s_%(class)s_created",
        on_delete=models.SET_NULL,
        null=True,
        editable=False
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Updated by"),
        related_name="%(app_label)s_%(class)s_updated",
        on_delete=models.SET_NULL,
        null=True,
        editable=False
    )
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True

class Category(UserStampedModel):
    name = models.CharField(_("Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

class Option(UserStampedModel):
    category = models.ForeignKey(Category, verbose_name=_("Category"), related_name="options", on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=100)
    value = models.CharField(_("Value"), max_length=255, blank=True, null=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    parent = models.ForeignKey("self", verbose_name=_("Parent"), blank=True, null=True, related_name="children", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Option")
        verbose_name_plural = _("Options")
        ordering = ['category', 'order', 'name']
        unique_together = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"