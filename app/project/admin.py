# admin.py
from django.db.models import Count
from .models import *
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog


class BaseInline(admin.TabularInline):
    extra = 0
    classes = ['collapse']
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

    def save_model(self, request, obj, form, change):
        if not change:
            obj._current_user = request.user
        super().save_model(request, obj, form, change)

class ProjectMemberInline(BaseInline):
    model = ProjectMember
    fk_name = 'project'
    autocomplete_fields = ['user']
    fields = ('user', 'role', 'joined_at')
    readonly_fields = ('joined_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

class TaskInline(BaseInline):
    model = Task
    fk_name = 'project'
    fields = ('code', 'title', 'status', 'assigned_to', 'due_date')
    autocomplete_fields = ['assigned_to']
    readonly_fields = ('code',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assigned_to')


class ResearchDataInline(BaseInline):
    model = ResearchData
    fk_name = 'project'
    fields = ('title', 'data_type', 'collection_date', 'responsible_person')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('responsible_person')


class ProgressInline(BaseInline):
    model = Progress
    fk_name = 'project'
    fields = ('title', 'progress_type', 'status', 'due_date', 'completion_date')




@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status_badge', 'progress_bar', 'team_count',
                    'start_date', 'end_date', 'created_by', 'created_at')
    list_filter = ('status', 'public_project', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'progress_display')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    inlines = [
        ProjectMemberInline,
        TaskInline,
        ProgressInline,

        ResearchDataInline,

    ]

    fieldsets = (
        ('Project Information', {
            'fields': (
                'title',
                'description',
                'status',
                'progress_display',
                'public_project'
            )
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Audit Information', {
            'fields': (
                ('created_by', 'created_at'),
                ('updated_by', 'updated_at')
            ),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'created_by',
            'updated_by'
        ).annotate(
            member_count=Count('team_members', distinct=True)  # Changed this line
        )

    def team_count(self, obj):
        return f'{obj.member_count} member{"s" if obj.member_count != 1 else ""}'

    team_count.short_description = 'Team Size'
    team_count.admin_order_field = 'member_count'

    def progress_display(self, obj):
        stats = obj.get_task_stats()
        progress = obj.progress
        color = '#28a745' if progress >= 70 else '#ffc107' if progress >= 40 else '#dc3545'

        return format_html(
            '<div style="margin: 10px 0;">'
            '<strong>Progress: {}%</strong><br>'
            '<div style="width: 200px; height: 20px; background-color: #f8f9fa; '
            'border: 1px solid #dee2e6; margin: 5px 0;">'
            '<div style="width: {}%; height: 100%; background-color: {}; '
            'text-align: center; line-height: 20px; color: white;">{}%</div>'
            '</div>'
            '<br><strong>Task Statistics:</strong><br>'
            'Total Tasks: {}<br>'
            'Completed: {}<br>'
            'In Progress: {}<br>'
            'Pending: {}<br>'
            '</div>',
            progress, progress, color, progress,
            stats['total'],
            stats['completed'],
            stats['in_progress'],
            stats['pending']
        )

    progress_display.short_description = 'Project Progress'

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
            '<div style="width: 100px; height: 20px; background-color: #f8f9fa; '
            'border: 1px solid #dee2e6;">'
            '<div style="width: {}%; height: 100%; background-color: {}; '
            'text-align: center; line-height: 20px; color: white; '
            'font-size: 12px;">{}</div></div>',
            progress, color, f"{progress}%"
        )

    progress_bar.short_description = 'Progress'

    def save_model(self, request, obj, form, change):
        obj._current_user = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance._current_user = request.user
            instance.save()
        formset.save_m2m()


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
    list_display = ('title','code', 'project_link', 'status', 'assigned_to', 'due_date')
    list_filter = ('status', 'project', 'assigned_to')
    search_fields = ('title', 'description', 'project__title')
    autocomplete_fields = ['project', 'assigned_to']
    readonly_fields = ('created_at', 'updated_at')

    def project_link(self, obj):
        url = reverse('admin:project_project_change', args=[obj.project.id])
        return format_html('<a href="{}">{}</a>', url, obj.project.title)

    project_link.short_description = 'Project'




@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'actor_link',
        'action_type',
        'project_link',
        'content_type',
        'object_link',
        'short_description'
    ]

    list_filter = [
        'action_type',
        'timestamp',
        'content_type',
        ('project', admin.RelatedOnlyFieldListFilter),
        ('actor', admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = [
        'description',
        'actor__username',
        'actor__email',
        'project__title',
    ]

    readonly_fields = [
        'timestamp',
        'actor',
        'action_type',
        'content_type',
        'object_id',
        'project',
        'description',
        'changes_prettified',
    ]

    date_hierarchy = 'timestamp'

    fieldsets = (
        (None, {
            'fields': (
                'timestamp',
                'actor',
                'action_type',
                'project',
            )
        }),
        ('Action Details', {
            'fields': (
                'content_type',
                'object_id',
                'description',
                'changes_prettified',
            )
        }),
    )

    def get_queryset(self, request):
        """Optimize queries by prefetching related fields"""
        return super().get_queryset(request).select_related(
            'actor',
            'project',
            'content_type'
        )

    def actor_link(self, obj):
        """Create a link to the user admin"""
        if obj.actor:
            url = reverse(
                f'admin:{obj.actor._meta.app_label}_{obj.actor._meta.model_name}_change',
                args=[obj.actor.id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.actor)
        return '-'

    actor_link.short_description = 'Actor'
    actor_link.admin_order_field = 'actor'

    def project_link(self, obj):
        """Create a link to the project admin"""
        if obj.project:
            url = reverse(
                f'admin:{obj.project._meta.app_label}_{obj.project._meta.model_name}_change',
                args=[obj.project.id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.project)
        return '-'

    project_link.short_description = 'Project'
    project_link.admin_order_field = 'project'

    def object_link(self, obj):
        """Create a link to the related object's admin"""
        if obj.content_type and obj.object_id:
            try:
                related_object = obj.content_type.get_object_for_this_type(pk=obj.object_id)
                url = reverse(
                    f'admin:{related_object._meta.app_label}_{related_object._meta.model_name}_change',
                    args=[obj.object_id]
                )
                return format_html('<a href="{}">{}</a>', url, str(related_object))
            except Exception:
                return f'Object not found ({obj.object_id})'
        return '-'

    object_link.short_description = 'Related Object'

    def short_description(self, obj):
        """Display a truncated version of the description"""
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description

    short_description.short_description = 'Description'

    def changes_prettified(self, obj):
        """Display the changes in a more readable format"""
        if not obj.changes:
            return '-'

        html = ['<table style="width: 100%;">']

        if isinstance(obj.changes, dict):
            # Handle different types of changes based on action_type
            if obj.action_type == 'status_change':
                html.append(
                    f'<tr><th>From Status:</th><td>{obj.changes.get("from_status", "-")}</td></tr>'
                    f'<tr><th>To Status:</th><td>{obj.changes.get("to_status", "-")}</td></tr>'
                )
            elif 'changed_fields' in obj.changes:
                for change in obj.changes['changed_fields']:
                    html.append(
                        f'<tr>'
                        f'<th>{change["field"]}:</th>'
                        f'<td>From "{change["from"]}" to "{change["to"]}"</td>'
                        f'</tr>'
                    )
            else:
                # Generic handling for other types of changes
                for key, value in obj.changes.items():
                    html.append(f'<tr><th>{key}:</th><td>{value}</td></tr>')

        html.append('</table>')
        return format_html(''.join(html))

    changes_prettified.short_description = 'Changes'

    def has_add_permission(self, request):
        """Disable manual creation of logs"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of logs"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Control deletion of logs based on user permissions"""
        return request.user.is_superuser


@admin.register(ProjectFunding)
class ProjectFundingAdmin(admin.ModelAdmin):
    list_display = ('project', 'get_source', 'amount', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('project__title', 'grant__title', 'budget__title')
    raw_id_fields = ('project', 'grant', 'budget')

    def get_source(self, obj):
        return obj.grant or obj.budget

    get_source.short_description = 'Funding Source'


@admin.register(ProjectBudgetLine)
class ProjectBudgetLineAdmin(admin.ModelAdmin):
    list_display = ('project', 'category', 'amount', 'timeline', 'get_used_amount', 'get_remaining')
    list_filter = ('category', 'project', 'timeline')
    search_fields = ('project__title', 'description')
    raw_id_fields = ('project', 'project_funding', 'cost_center', 'responsible_person')

    def get_used_amount(self, obj):
        used = obj.expenses.filter(status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
        return format_html('<span style="color: {};">{}</span>',
                           'red' if used > obj.amount else 'green',
                           used)

    get_used_amount.short_description = 'Used Amount'

    def get_remaining(self, obj):
        used = obj.expenses.filter(status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
        remaining = obj.amount - used
        return format_html('<span style="color: {};">{}</span>',
                           'red' if remaining < 0 else 'green',
                           remaining)

    get_remaining.short_description = 'Remaining'


@admin.register(ProjectExpense)
class ProjectExpenseAdmin(admin.ModelAdmin):
    list_display = ('project', 'budget_line', 'amount', 'status', 'expense_date', 'submitted_by')
    list_filter = ('status', 'expense_date', 'project')
    search_fields = ('project__title', 'description', 'submitted_by__username')
    raw_id_fields = ('project', 'budget_line', 'submitted_by', 'approved_by')
    readonly_fields = ('submitted_date', 'approved_date')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.submitted_by = request.user
        if 'status' in form.changed_data:
            if obj.status == 'APPROVED':
                obj.approved_by = request.user
                obj.approved_date = timezone.now()
            elif obj.status == 'SUBMITTED':
                obj.submitted_date = timezone.now()
        super().save_model(request, obj, form, change)