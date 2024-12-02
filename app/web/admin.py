from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *


class AttachmentInline(GenericTabularInline):
    model = Attachment
    extra = 1
    fields = ('file', 'description')


class BaseDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def get_image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.featured_image.url)
        return "No image"

    get_image_preview.short_description = 'Image Preview'


@admin.register(SOP)
class SOPAdmin(BaseDocumentAdmin):
    list_display = ('sop_number', 'title', 'department', 'status', 'effective_date', 'version', 'get_image_preview')
    list_filter = BaseDocumentAdmin.list_filter + ('status', 'department', 'effective_date')
    search_fields = BaseDocumentAdmin.search_fields + ('sop_number', 'department')
    inlines = [AttachmentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('sop_number', 'title', 'department', 'status')
        }),
        ('Dates', {
            'fields': ('effective_date', 'review_date')
        }),
        ('Content', {
            'fields': ('content', 'version', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(News)
class NewsAdmin(BaseDocumentAdmin):
    list_display = ('title', 'publish_date', 'is_published', 'get_image_preview', 'get_categories')
    list_filter = BaseDocumentAdmin.list_filter + ('is_published', 'categories')
    inlines = [AttachmentInline]
    filter_horizontal = ('categories',)

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    get_categories.short_description = 'Categories'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'excerpt', 'is_published')
        }),
        ('Content', {
            'fields': ('content', 'featured_image', 'categories')
        }),
        ('Publication', {
            'fields': ('publish_date',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(Bulletin)
class BulletinAdmin(BaseDocumentAdmin):
    list_display = ('title', 'priority', 'is_active', 'expiry_date', 'get_image_preview')
    list_filter = BaseDocumentAdmin.list_filter + ('priority', 'is_active')
    inlines = [AttachmentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'priority', 'is_active')
        }),
        ('Content', {
            'fields': ('content', 'featured_image')
        }),
        ('Expiry', {
            'fields': ('expiry_date',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'description', 'uploaded_at', 'content_type', 'object_id')
    list_filter = ('uploaded_at', 'content_type')
    search_fields = ('description',)
    date_hierarchy = 'uploaded_at'

    def get_model_link(self, obj):
        if obj.content_object:
            url = reverse(
                f'admin:{obj.content_object._meta.app_label}_{obj.content_object._meta.model_name}_change',
                args=[obj.object_id]
            )
            return format_html('<a href="{}">{}</a>', url, str(obj.content_object))
        return "No link"

    get_model_link.short_description = 'Linked to'


class BaseHolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'is_recurring', 'created_by', 'created_at')
    list_filter = ('is_recurring', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    date_hierarchy = 'date'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PublicHoliday)
class PublicHolidayAdmin(BaseHolidayAdmin):
    list_display = BaseHolidayAdmin.list_display + ('holiday_type', 'state')
    list_filter = BaseHolidayAdmin.list_filter + ('holiday_type',)
    search_fields = BaseHolidayAdmin.search_fields + ('state',)

    fieldsets = (
        ('Holiday Information', {
            'fields': ('name', 'description', 'date', 'is_recurring')
        }),
        ('Classification', {
            'fields': ('holiday_type', 'state')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(InternalHoliday)
class InternalHolidayAdmin(BaseHolidayAdmin):
    list_display = BaseHolidayAdmin.list_display + ('department', 'status', 'get_days_until')
    list_filter = BaseHolidayAdmin.list_filter + ('status', 'department')
    filter_horizontal = ('applicable_to',)

    def get_days_until(self, obj):
        days = obj.days_until()
        if days < 0:
            return format_html('<span style="color: red;">Past</span>')
        elif days == 0:
            return format_html('<span style="color: green;">Today</span>')
        else:
            return format_html('<span>{} days</span>', days)

    get_days_until.short_description = 'Days Until'

    fieldsets = (
        ('Holiday Information', {
            'fields': ('name', 'description', 'date', 'is_recurring')
        }),
        ('Application', {
            'fields': ('department', 'applicable_to', 'notification_days')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by', 'updated_at'),
            'classes': ('collapse',)
        })
    )