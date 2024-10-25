# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Project, ProjectMember, Task


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    autocomplete_fields = ['user']
    classes = ['collapse']
    fields = ('user', 'role', 'joined_at')
    readonly_fields = ('joined_at',)
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ('title', 'status', 'assigned_to', 'due_date')
    autocomplete_fields = ['assigned_to']
    classes = ['collapse']
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assigned_to')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status_badge', 'progress_bar', 'team_count',
                    'start_date', 'end_date', 'created_by', 'created_at')
    list_filter = ('status', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'created_by__email',
                     'team_members__email')
    readonly_fields = ('created_at', 'updated_at', 'progress_display')
    date_hierarchy = 'created_at'
    inlines = [ProjectMemberInline, TaskInline]

    fieldsets = (
        ('Project Information', {
            'fields': (
                'title',
                'description',
                'status',
                'progress_display'
            )
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'created_at', 'updated_at')
        }),
        ('Team', {
            'fields': ('created_by',),
            'description': 'Project team members can be managed in the section below.'
        })
    )

    def progress_display(self, obj):
        """Display progress information in the admin detail view"""
        stats = obj.get_task_stats()
        return format_html(
            '''
            <div style="margin-bottom: 10px;">
                <strong>Progress: {}%</strong>
                <div style="width: 200px; height: 20px; background-color: #f8f9fa; 
                            border-radius: 4px; overflow: hidden; margin: 5px 0;">
                    <div style="width: {}%; height: 100%; background-color: {}; 
                               text-align: center; color: white; line-height: 20px;">
                        {}%
                    </div>
                </div>
            </div>
            <div style="margin-top: 10px;">
                <strong>Task Statistics:</strong><br>
                Total Tasks: {}<br>
                Completed: {}<br>
                In Progress: {}<br>
                Pending: {}<br>
            </div>
            ''',
            obj.progress,
            obj.progress,
            '#28a745' if obj.progress >= 70 else '#ffc107' if obj.progress >= 40 else '#dc3545',
            obj.progress,
            stats['total'],
            stats['completed'],
            stats['in_progress'],
            stats['pending']
        )

    progress_display.short_description = 'Project Progress'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            team_member_count=Count('team_members', distinct=True),
        )
        return queryset

    def status_badge(self, obj):
        colors = {
            'planning': '#17a2b8',
            'active': '#28a745',
            'on_hold': '#ffc107',
            'completed': '#007bff',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def progress_bar(self, obj):
        progress = obj.progress
        color = '#28a745' if progress >= 70 else '#ffc107' if progress >= 40 else '#dc3545'
        return format_html(
            '''
            <div style="width: 100px; height: 20px; background-color: #f8f9fa; 
                        border-radius: 4px; overflow: hidden;">
                <div style="width: {}%; height: 100%; background-color: {}; 
                           text-align: center; color: white; font-size: 0.8em; 
                           line-height: 20px;">
                    {}%
                </div>
            </div>
            ''',
            progress,
            color,
            progress
        )

    progress_bar.short_description = 'Progress'

    def team_count(self, obj):
        count = obj.team_member_count
        return f'{count} member{"s" if count != 1 else ""}'

    team_count.short_description = 'Team Size'
    team_count.admin_order_field = 'team_member_count'

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
        js = ('js/custom_admin.js',)


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project_link', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name',
                     'project__title')
    autocomplete_fields = ['user', 'project']
    readonly_fields = ('joined_at',)

    def project_link(self, obj):
        url = reverse('admin:project_project_change', args=[obj.project.id])
        return format_html('<a href="{}">{}</a>', url, obj.project.title)

    project_link.short_description = 'Project'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_link', 'status', 'assigned_to', 'due_date')
    list_filter = ('status', 'project', 'assigned_to')
    search_fields = ('title', 'description', 'project__title')
    autocomplete_fields = ['project', 'assigned_to']
    readonly_fields = ('created_at', 'updated_at')

    def project_link(self, obj):
        url = reverse('admin:project_project_change', args=[obj.project.id])
        return format_html('<a href="{}">{}</a>', url, obj.project.title)

    project_link.short_description = 'Project'