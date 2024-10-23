from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.contrib.contenttypes.admin import GenericTabularInline
from app.finance.models import DocumentProof, JournalEntry, PosAllocation
from .models import (
    Project, ProjectMember, ProjectGrant, GrantReport,
    Publication, ResearchData, Event, Progress
)


class DocumentProofInline(GenericTabularInline):
    model = DocumentProof
    extra = 1
    readonly_fields = ('upload_date',)


class JournalEntryInline(GenericTabularInline):
    model = JournalEntry
    extra = 1
    readonly_fields = ('date',)


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    autocomplete_fields = ['member', 'pos_allocation']


class GrantReportInline(admin.TabularInline):
    model = GrantReport
    extra = 0
    readonly_fields = ('submitted_by',)


class PosAllocationInline(GenericTabularInline):
    model = PosAllocation
    extra = 1
    fields = ('name', 'amount', 'currency')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date',
                    'project_manager')
    list_filter = ('status', 'start_date', 'project_manager')
    search_fields = ('title', 'description', 'project_manager__username')
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'project_manager')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Financial', {
            'fields': ('budget', 'currency'),
        }),
    )

    inlines = [ProjectMemberInline, DocumentProofInline, JournalEntryInline]


@admin.register(ProjectGrant)
class ProjectGrantAdmin(admin.ModelAdmin):
    list_display = ('project', 'grant', 'status', 'submission_deadline')
    list_filter = ('status', 'submission_deadline')
    search_fields = ('project__title', 'grant__name')
    date_hierarchy = 'submission_deadline'

    inlines = [GrantReportInline, DocumentProofInline]


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_type', 'project', 'publication_date')
    list_filter = ('publication_type', 'publication_date', 'publisher')
    search_fields = ('title', 'abstract', 'citation')
    date_hierarchy = 'publication_date'
    filter_horizontal = ('authors',)
    inlines = [DocumentProofInline, PosAllocationInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')


@admin.register(ResearchData)
class ResearchDataAdmin(admin.ModelAdmin):
    list_display = ('title', 'data_type', 'project', 'collection_date',
                    'responsible_person')
    list_filter = ('data_type', 'collection_date')
    search_fields = ('title', 'description', 'methodology')
    date_hierarchy = 'collection_date'
    inlines = [DocumentProofInline, PosAllocationInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'project', 'responsible_person'
        )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'project', 'date', 'location',
                    'expected_participants')
    list_filter = ('event_type', 'date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'

    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'event_type', 'project', 'description')
        }),
        ('Logistics', {
            'fields': ('date', 'location', 'expected_participants',
                       'actual_participants')
        }),
    )

    inlines = [DocumentProofInline, PosAllocationInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'progress_type', 'due_date', 'status')
    list_filter = ('progress_type', 'due_date', 'status')
    search_fields = ('title', 'description', 'notes')
    date_hierarchy = 'due_date'
    inlines = [DocumentProofInline]

    fieldsets = (
        ('Progress Information', {
            'fields': ('title', 'project', 'progress_type', 'description')
        }),
        ('Status', {
            'fields': ('status', 'due_date', 'completion_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'attachments'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')


@admin.register(GrantReport)
class GrantReportAdmin(admin.ModelAdmin):
    list_display = ('project_grant', 'report_date', 'submitted_by', 'approved')
    list_filter = ('report_date', 'approved')
    search_fields = ('project_grant__project__title', 'narrative')
    date_hierarchy = 'report_date'
    inlines = [DocumentProofInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'project_grant', 'submitted_by'
        )


# Admin Site Configuration
admin.site.site_header = 'NGO Management System'
admin.site.site_title = 'NGO Management Portal'
admin.site.index_title = 'Administration Dashboard'