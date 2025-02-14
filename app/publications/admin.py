from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import (
    Publication,
    PublicationCategory,
    PublicationAuthor,
    PublicationTrackingEvent,
    PublicationStats
)


class PublicationAuthorInline(admin.TabularInline):
    model = PublicationAuthor
    extra = 1
    ordering = ['order']
    autocomplete_fields = ['author']
    fields = ['author', 'order', 'is_corresponding', 'affiliation']


class PublicationStatsInline(admin.StackedInline):
    model = PublicationStats
    can_delete = False
    readonly_fields = [
        'daily_views', 'daily_downloads', 'last_daily_update',
        'weekly_views', 'weekly_downloads', 'last_weekly_update',
        'monthly_views', 'monthly_downloads', 'last_monthly_update'
    ]
    max_num = 0
    verbose_name_plural = 'Publication Statistics'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'get_authors', 'category', 'date_publish',
        'status', 'publish', 'highlight', 'viewed',
        'get_daily_downloads', 'get_monthly_views'
    ]
    list_filter = ['status', 'publish', 'highlight', 'category']
    search_fields = ['title', 'description', 'authors__first_name', 'authors__last_name']
    filter_horizontal = ['editor', 'partners', 'topic']
    readonly_fields = [
        'slug', 'viewed', 'download_count',
        'get_tracking_summary'
    ]
    inlines = [PublicationAuthorInline, PublicationStatsInline]
    date_hierarchy = 'date_publish'

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'date_publish')
        }),
        ('Classification', {
            'fields': ('category', 'topic', 'tags')
        }),
        ('Project & Contributors', {
            'fields': ('project', 'editor', 'partners', 'added_by')
        }),
        ('Media', {
            'fields': ('image', 'image_credit', 'cover', 'file')
        }),
        ('Status', {
            'fields': ('status', 'publish', 'highlight')
        }),
        ('Statistics', {
            'fields': ('viewed', 'download_count', 'get_tracking_summary'),
            'classes': ('collapse',)
        })
    )

    def get_authors(self, obj):
        authors = obj.get_author_list()
        if not authors:
            return "-"
        shown_authors = authors[:3]
        if len(authors) > 3:
            return f"{', '.join(shown_authors)} ..."
        return ", ".join(shown_authors)
    get_authors.short_description = "Authors"

    def get_daily_downloads(self, obj):
        stats = obj.current_stats
        return f"{stats.daily_downloads} today"

    get_daily_downloads.short_description = "Today's Downloads"

    def get_monthly_views(self, obj):
        stats = obj.current_stats
        return f"{stats.monthly_views} this month"

    get_monthly_views.short_description = "Monthly Views"

    def get_tracking_summary(self, obj):
        stats = obj.current_stats
        summary = f"""
        <div style="margin-bottom: 10px;">
            <h4>Today's Statistics:</h4>
            Views: {stats.daily_views} | Downloads: {stats.daily_downloads}
        </div>
        <div style="margin-bottom: 10px;">
            <h4>This Week's Statistics:</h4>
            Views: {stats.weekly_views} | Downloads: {stats.weekly_downloads}
        </div>
        <div style="margin-bottom: 10px;">
            <h4>This Month's Statistics:</h4>
            Views: {stats.monthly_views} | Downloads: {stats.monthly_downloads}
        </div>
        """
        return format_html(summary)

    get_tracking_summary.short_description = "Tracking Summary"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category',
            'project',
            'added_by',
            'stats'
        ).prefetch_related(
            'authors',
            'editor',
            'partners',
            'topic',
            'publicationauthor_set',  # Add this to optimize author queries
            'publicationauthor_set__author'  # And this for author details
        )

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PublicationTrackingEvent)
class PublicationTrackingEventAdmin(admin.ModelAdmin):
    list_display = [
        'publication', 'event_type', 'timestamp', 'user',
        'ip_address'
    ]
    list_filter = ['event_type', 'timestamp', 'publication']
    search_fields = [
        'publication__title', 'user__username',
        'ip_address', 'user_agent'
    ]
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PublicationStats)
class PublicationStatsAdmin(admin.ModelAdmin):
    list_display = [
        'publication', 'daily_views', 'daily_downloads',
        'monthly_views', 'monthly_downloads',
        'get_last_update'
    ]
    search_fields = ['publication__title']
    readonly_fields = [
        'daily_views', 'daily_downloads', 'last_daily_update',
        'weekly_views', 'weekly_downloads', 'last_weekly_update',
        'monthly_views', 'monthly_downloads', 'last_monthly_update'
    ]

    def get_last_update(self, obj):
        if obj.last_daily_update:
            return obj.last_daily_update.strftime('%Y-%m-%d %H:%M')
        return '-'

    get_last_update.short_description = 'Last Updated'

    def has_add_permission(self, request):
        return False

    actions = ['update_statistics']

    def update_statistics(self, request, queryset):
        for stats in queryset:
            stats.update_stats()
        self.message_user(request, f"Updated statistics for {queryset.count()} publications.")

    update_statistics.short_description = "Update statistics for selected publications"


@admin.register(PublicationCategory)
class PublicationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_publication_count']
    search_fields = ['name', 'description']
    readonly_fields = ['slug']

    def get_publication_count(self, obj):
        return obj.publications.count()

    get_publication_count.short_description = 'Publications'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            pub_count=Count('publications')
        )


@admin.register(PublicationAuthor)
class PublicationAuthorAdmin(admin.ModelAdmin):
    list_display = ['author', 'publication', 'order', 'is_corresponding', 'affiliation']
    list_filter = ['is_corresponding']
    search_fields = [
        'author__first_name',
        'author__last_name',
        'publication__title'
    ]
    autocomplete_fields = ['author', 'publication']
    ordering = ['publication', 'order']
    list_select_related = ['author', 'publication']