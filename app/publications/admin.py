from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Publication, PublicationCategory, PublicationAuthor


class PublicationAuthorInline(admin.TabularInline):
    model = PublicationAuthor
    extra = 1
    ordering = ['order']
    autocomplete_fields = ['author']
    fields = ['author', 'order', 'is_corresponding', 'affiliation']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_authors', 'category', 'date_publish', 'status', 'publish', 'highlight', 'viewed']
    list_filter = ['status', 'publish', 'highlight', 'category']
    search_fields = ['title', 'description', 'authors__first_name', 'authors__last_name']
    filter_horizontal = ['editor', 'partners', 'topic']
    readonly_fields = ['slug', 'viewed', 'download_count']
    inlines = [PublicationAuthorInline]
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
            'fields': ('status', 'publish', 'highlight', 'viewed', 'download_count')
        })
    )

    def get_authors(self, obj):
        authors = obj.get_author_list()
        if authors:
            return ", ".join(authors[:3]) + ("..." if len(authors) > 3 else "")
        return "-"

    get_authors.short_description = "Authors"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category',
            'project',
            'added_by'
        ).prefetch_related('authors', 'editor', 'partners', 'topic')

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


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