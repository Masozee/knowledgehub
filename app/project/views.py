from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView, View
from django.db.models.functions import Lower, Substr, Concat
from django.db.models import CharField, Count, Q, Prefetch
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .forms import *
from django.views.decorators.csrf import csrf_protect
import json
from app.project.mixins import *
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Project, ProjectMember
from app.publications.models import Publication
from app.events.models import Event, Speaker
from django.shortcuts import render



class PermissionMixin:
    """
    Custom mixin to handle permission checks for project-related views
    """

    def dispatch(self, request, *args, **kwargs):
        # Get the project first
        project_uuid = self.kwargs.get('project_uuid')
        self.project = get_object_or_404(Project, uuid=project_uuid)

        # Check if user has permission
        if not self.has_permission():
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('project:project_detail', uuid=project_uuid)

        return super().dispatch(request, *args, **kwargs)

    def has_permission(self):
        # Default implementation - override in specific views
        return True

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'dashboard/project/index.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        # Enhance prefetch_related to include user details and exclude project lead
        queryset = Project.objects.select_related('created_by') \
            .prefetch_related(
            Prefetch(
                'projectmember_set',
                queryset=ProjectMember.objects.select_related('user')
                .exclude(role='owner')
                .annotate(
                    initials=Concat(
                        Substr('user__first_name', 1, 1),
                        Substr('user__last_name', 1, 1),
                        output_field=CharField()
                    )
                )
            ),
            'progress_items'
        )

        # Handle filtering
        filter_param = self.request.GET.get('filter')
        if filter_param:
            queryset = queryset.filter(status=filter_param)

        # Handle search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get user projects efficiently with a single query
        user_projects = Project.objects.filter(
            Q(created_by=self.request.user) |
            Q(team_members=self.request.user)
        ).distinct()

        # Use conditional aggregation for status counts
        project_stats = user_projects.aggregate(
            total_projects=Count('id'),
            active_projects=Count('id', filter=Q(status='active')),
            completed_projects=Count('id', filter=Q(status='completed')),
            on_hold_projects=Count('id', filter=Q(status='on_hold')),
            cancelled_projects=Count('id', filter=Q(status='cancelled'))
        )

        # Get available team members (excluding the current user)
        available_users = get_user_model().objects.exclude(
            id=self.request.user.id
        ).annotate(
            initials=Concat(
                Substr('first_name', 1, 1),
                Substr('last_name', 1, 1),
                output_field=CharField()
            )
        )

        context.update({
            **project_stats,
            'users': available_users,
        })
        return context

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Create project
                project = Project.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date'),
                    created_by=request.user
                )

                # Add team members with roles (excluding owner)
                team_members = request.POST.getlist('team_members')
                if team_members:
                    ProjectMember.objects.bulk_create([
                        ProjectMember(
                            project=project,
                            user_id=user_id,
                            role='member'
                        ) for user_id in team_members
                    ])

                # Add creator as owner
                ProjectMember.objects.create(
                    project=project,
                    user=request.user,
                    role='owner'
                )

                # Create initial progress item if specified
                if request.POST.get('initial_milestone'):
                    Progress.objects.create(
                        project=project,
                        title=request.POST.get('initial_milestone'),
                        progress_type='milestone',
                        description=request.POST.get('milestone_description', ''),
                        due_date=project.end_date,
                        responsible_person=request.user,
                        status=0
                    )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': project.uuid,
                })
            return redirect('project:index')

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            return redirect('project:project_list')

@require_POST
def mark_project_complete(request, uuid):
    try:
        project = Project.objects.select_related('created_by') \
            .prefetch_related('team_members') \
            .get(uuid=uuid)

        # Check if user has permission
        member = project.projectmember_set.filter(
            user=request.user,
            role__in=['owner', 'manager']
        ).first()

        if not member and project.created_by != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied. Only project owners and managers can complete projects.'
            }, status=403)

        project.status = 'completed'
        project.save()

        # Complete any remaining progress items
        Progress.objects.filter(
            project=project,
            completion_date__isnull=True
        ).update(
            completion_date=timezone.now().date(),
            status=100
        )

        return JsonResponse({
            'success': True,
            'message': 'Project marked as complete successfully'
        })
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'dashboard/project/detail.html'
    context_object_name = 'project'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_queryset(self):
        return Project.objects.select_related('created_by').prefetch_related(
            'team_members',
            'progress_items',

            'research_data',

            Prefetch(
                'activity_logs',
                queryset=ActivityLog.objects.select_related(
                    'actor',
                    'content_type'
                ).filter(
                    actor__isnull=False
                ).order_by('-timestamp')
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Get team members with roles
        team_members = ProjectMember.objects.filter(
            project=project
        ).select_related('user').order_by('role', 'joined_at')

        # Get activity logs for this project and related objects
        activity_logs = project.activity_logs.select_related(
            'actor',
            'content_type'
        ).order_by('-timestamp')[:10]

        # Group activities by date for better organization
        grouped_activities = {}
        for log in activity_logs:
            date = log.timestamp.date()
            if date not in grouped_activities:
                grouped_activities[date] = []
            grouped_activities[date].append(log)

        # Get progress statistics
        progress_stats = Progress.objects.filter(project=project).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status=100)),
            in_progress=Count('id', filter=Q(status__gt=0, status__lt=100)),
            not_started=Count('id', filter=Q(status=0))
        )

        # Calculate overall progress
        total_progress = progress_stats['total']
        overall_progress = (progress_stats['completed'] / total_progress * 100) if total_progress > 0 else 0

        context.update({
            'team_members': team_members,
            'progress_items': project.progress_items.all(),
            'progress_stats': progress_stats,
            'overall_progress': overall_progress,

            'research_data': project.research_data.all(),

            'member_roles': ProjectMember._meta.get_field('role').choices,
            'progress_types': Progress.PROGRESS_TYPES,
            'activity_logs': activity_logs,
            'grouped_activities': grouped_activities,
            'can_edit': self.request.user == project.created_by or project.projectmember_set.filter(
                user=self.request.user,
                role__in=['owner', 'manager']
            ).exists()
        })
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    template_name = 'dashboard/project/create.html'
    form_class = ProjectCreateForm
    success_url = reverse_lazy('project:project_list')

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs
        except Exception as e:
            messages.error(self.request, f'Form kwargs error: {str(e)}')
            return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Project created successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'Form validation error: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'dashboard/project/create.html'
    form_class = ProjectUpdateForm
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class TaskKanbanView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'dashboard/project/task_kanban.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        self.project = get_object_or_404(Project, uuid=self.kwargs['project_uuid'])
        return Task.objects.filter(project=self.project).select_related(
            'assigned_to',
            'created_by',
            'project'
        ).order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = self.get_queryset()

        def get_user_initials(user):
            """Helper function to get user initials"""
            if not user:
                return 'UN'
            if user.first_name and user.last_name:
                return f"{user.first_name[0]}{user.last_name[0]}".upper()
            elif user.first_name:
                return user.first_name[0].upper()
            elif user.last_name:
                return user.last_name[0].upper()
            return user.username[0].upper() if user.username else 'U'

        def prepare_tasks(task_list):
            return [
                {
                    'id': str(task.id),
                    'title': f"""
                        <div class="kanban-item-title">
                            <h6 class="title">[{task.code}] {task.title}</h6>
                            <div class="drodown">
                                <a href="#" class="dropdown-toggle" data-bs-toggle="dropdown">
                                    <div class="user-avatar-group">
                                        <div class="user-avatar xs bg-primary">
                                            <span>{get_user_initials(task.assigned_to)}</span>
                                        </div>
                                    </div>
                                </a>
                                <div class="dropdown-menu dropdown-menu-end">
                                    <ul class="link-list-opt no-bdr p-3 g-2">
                                        <li>
                                            <div class="user-card">
                                                <div class="user-avatar sm bg-primary">
                                                    <span>{get_user_initials(task.assigned_to)}</span>
                                                </div>
                                                <div class="user-name">
                                                    <span class="tb-lead">{task.assigned_to if task.assigned_to else 'Unassigned'}</span>
                                                </div>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="kanban-item-text">
                            <p>{task.description[:100] + '...' if task.description and len(task.description) > 100 else task.description or 'No description'}</p>
                        </div>
                        <div class="kanban-item-meta">
                            <ul class="kanban-item-meta-list">
                                <li class="text-{'danger' if task.is_overdue else 'warning' if task.due_date else 'soft'}">
                                    <em class="icon ni ni-calendar"></em>
                                    <span>{'Due: ' + task.due_date.strftime('%d %b %Y') if task.due_date else 'No due date'}</span>
                                </li>
                            </ul>
                            <ul class="kanban-item-meta-list">
                                <li><em class="icon ni ni-notes"></em><span>Task</span></li>
                            </ul>
                        </div>
                    """,
                    'update_url': reverse('project:task_update_status', kwargs={
                        'project_uuid': task.project.uuid,
                        'code': task.code
                    })
                } for task in task_list
            ]

        kanban_data = [
            {
                'id': 'pending',
                'title': 'Pending',
                'class': 'kanban-light',
                'item': prepare_tasks(tasks.filter(status='pending'))
            },
            {
                'id': 'in_progress',
                'title': 'In Progress',
                'class': 'kanban-primary',
                'item': prepare_tasks(tasks.filter(status='in_progress'))
            },
            {
                'id': 'completed',
                'title': 'Completed',
                'class': 'kanban-success',
                'item': prepare_tasks(tasks.filter(status='completed'))
            }
        ]

        context.update({
            'project': self.project,
            'kanban_data': json.dumps(kanban_data),
            'task_stats': self.project.get_task_stats(),
            'can_create': self.project.can_user_edit(self.request.user),
            'create_url': reverse('project:task_create', kwargs={'project_uuid': self.project.uuid})
        })
        return context

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'dashboard/project/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        self.project = get_object_or_404(Project, uuid=self.kwargs['project_uuid'])
        return Task.objects.filter(project=self.project).select_related(
            'assigned_to',
            'created_by'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['task_stats'] = self.project.get_task_stats()
        context['can_create'] = self.project.can_user_edit(self.request.user)
        return context

class TaskCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    model = Task
    template_name = 'dashboard/project/task_form.html'
    fields = ['title', 'description', 'status', 'assigned_to', 'due_date']

    def has_permission(self):
        return self.project.can_user_edit(self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['assigned_to'].queryset = self.project.team_members.all()
        return form

    def form_valid(self, form):
        form.instance.project = self.project
        form.instance._current_user = self.request.user
        messages.success(self.request, 'Task created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['action'] = 'Create'
        return context

class TaskUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    model = Task
    template_name = 'dashboard/project/task_form.html'
    fields = ['title', 'description', 'status', 'assigned_to', 'due_date']
    context_object_name = 'task'

    def get_object(self):
        return get_object_or_404(
            Task,
            project__uuid=self.kwargs['project_uuid'],
            code=self.kwargs['code']
        )

    def has_permission(self):
        return self.get_object().can_user_edit(self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['assigned_to'].queryset = self.object.project.team_members.all()
        return form

    def form_valid(self, form):
        form.instance._current_user = self.request.user
        messages.success(self.request, 'Task updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        context['action'] = 'Update'
        return context

class TaskDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    model = Task
    template_name = 'dashboard/project/task_confirm_delete.html'
    context_object_name = 'task'

    def get_object(self):
        return get_object_or_404(
            Task,
            project__uuid=self.kwargs['project_uuid'],
            code=self.kwargs['code']
        )

    def has_permission(self):
        return self.get_object().can_user_edit(self.request.user)

    def get_success_url(self):
        messages.success(self.request, 'Task deleted successfully.')
        return reverse_lazy('project:task_list', kwargs={
            'project_uuid': self.object.project.uuid
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'dashboard/project/task_detail.html'
    context_object_name = 'task'

    def get_object(self):
        return get_object_or_404(
            Task.objects.select_related(
                'project',
                'assigned_to',
                'created_by'
            ),
            project__uuid=self.kwargs['project_uuid'],
            code=self.kwargs['code']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object

        # Get activity logs for this task using content type
        activity_logs = ActivityLog.objects.filter(
            content_type__model='task',
            object_id=str(task.id)
        ).select_related(
            'actor',
            'content_type'
        ).order_by('-timestamp')[:10]

        # Group activities by date
        grouped_activities = {}
        for log in activity_logs:
            date = log.timestamp.date()
            if date not in grouped_activities:
                grouped_activities[date] = []
            grouped_activities[date].append(log)

        context.update({
            'project': task.project,
            'activity_logs': activity_logs,
            'grouped_activities': grouped_activities,
            'can_edit': task.can_user_edit(self.request.user)
        })
        return context

class ProjectFundUsageView(DetailView):
    template_name = 'dashboard/project/fund_usage.html'
    context_object_name = 'project'

    def get_object(self):
        # Store the project as self.project so we can use it in get_context_data
        self.project = get_object_or_404(Project, uuid=self.kwargs['project_uuid'])
        return self.project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'total_budget': self.project.get_total_budget(),
            'total_expenses': self.project.get_total_expenses(),
            'remaining_budget': self.project.get_remaining_budget(),
            # Add project UUID to context if needed for URLs
            'project_uuid': self.project.uuid
        })

        return context

class ProjectTeamView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/project/member.html'
    context_object_name = 'team_members'

    def get_queryset(self):
        self.project = get_object_or_404(Project, uuid=self.kwargs['project_uuid'])
        return ProjectMember.objects.filter(project=self.project).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['available_roles'] = ProjectMember._meta.get_field('role').choices
        return context

class InviteMemberView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ProjectMember
    template_name = 'project/team/invite_member.html'
    fields = ['user', 'role']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.project = get_object_or_404(Project, uuid=kwargs['project_uuid'])

    def test_func(self):
        return self.request.user == self.project.created_by or \
            self.project.projectmember_set.filter(
                user=self.request.user,
                role__in=['owner', 'manager']
            ).exists()

    def form_valid(self, form):
        form.instance.project = self.project
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project:team', kwargs={'project_uuid': self.project.uuid})

class ProjectOutreachView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/project/outreach.html'
    context_object_name = 'outreach_items'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project = get_object_or_404(
                Project.objects.select_related('created_by'),
                uuid=self.kwargs.get('project_uuid')
            )

            if not self.project.public_project and not (
                    request.user == self.project.created_by or
                    self.project.team_members.filter(id=request.user.id).exists()
            ):
                raise PermissionDenied("You don't have permission to view this project's outreach activities.")

            return super().dispatch(request, *args, **kwargs)

        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('project:project_list')
        except Exception as e:
            messages.error(request, f"Error accessing project outreach: {str(e)}")
            return redirect('project:project_list')

    def get_queryset(self):
        outreach_items = []

        # Get and process events
        for event in Event.objects.filter(
                project=self.project,
                status='published'
            ).select_related('category').prefetch_related(
                Prefetch('event_speakers',
                queryset=Speaker.objects.select_related('person').order_by('order'))
            ):
            outreach_items.append({
                'type': 'event',
                'date': event.start_date.date(),
                'title': event.title,
                'description': event.description,
                'location': event.location,
                'url': f'/events/{event.slug}/',
                'speakers': [{
                    'name': speaker.person.get_full_name,
                    'role': speaker.get_speaker_type_display()
                } for speaker in event.event_speakers.all()],
                'category': event.category.name if event.category else None,
                'status': event.status
            })

        # Get and process publications
        for publication in Publication.objects.filter(
                project=self.project,
                status='published',
                publish=True
            ).select_related('category').prefetch_related('authors'):
            if publication.date_publish:
                outreach_items.append({
                    'type': 'publication',
                    'date': publication.date_publish,
                    'title': publication.title,
                    'description': publication.description,
                    'url': f'/publications/{publication.slug}/',
                    'authors': [author.get_full_name for author in publication.authors.all()],
                    'category': publication.category.name if publication.category else None,
                    'download_count': publication.download_count
                })

        return sorted(outreach_items, key=lambda x: x['date'], reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project

        # Compute summary statistics
        context['stats'] = {
            'total_events': Event.objects.filter(
                project=self.project,
                status='published'
            ).count(),
            'total_publications': Publication.objects.filter(
                project=self.project,
                status='published',
                publish=True
            ).count(),
            'upcoming_events': Event.objects.filter(
                project=self.project,
                status='published',
                start_date__gt=timezone.now()
            ).count()
        }

        # Add permissions
        context.update({
            'can_create_event': self.project.can_user_edit(self.request.user),
            'can_create_publication': self.project.can_user_edit(self.request.user),
        })

        return context

class ResearchDataListView(LoginRequiredMixin, ListView):
    model = ResearchData
    template_name = 'dashboard/project/download.html'
    context_object_name = 'research_data_list'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project = get_object_or_404(
                Project.objects.select_related('created_by'),
                uuid=self.kwargs.get('project_uuid')
            )

            if not self.project.public_project and not (
                    request.user == self.project.created_by or
                    self.project.team_members.filter(id=request.user.id).exists()
            ):
                raise PermissionDenied("You don't have permission to view this project's research data.")

            return super().dispatch(request, *args, **kwargs)

        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('project:project_list')
        except Exception as e:
            messages.error(request, f"Error accessing project research data: {str(e)}")
            return redirect('project:project_list')

    def get_queryset(self):
        return ResearchData.objects.filter(
            project=self.project
        ).select_related(
            'responsible_person',
            'project'
        ).order_by('-collection_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project

        # Add statistics
        context['stats'] = {
            'total_data': ResearchData.objects.filter(project=self.project).count(),
            'recent_data': ResearchData.objects.filter(
                project=self.project,
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
            'data_types': ResearchData.objects.filter(
                project=self.project
            ).values('data_type').distinct().count()
        }

        # Add permissions
        context.update({
            'can_create_data': self.project.can_user_edit(self.request.user),
            'data_types': ResearchData.DATA_TYPES
        })

        return context


class ProjectConfigView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/project/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, uuid=self.kwargs['project_uuid'])

        context.update({
            'project': project,
            'recent_logs': project.activity_logs.select_related('actor')[:5],
            'total_budget': project.get_total_budget(),
            'remaining_budget': project.get_remaining_budget(),
            'funding_sources': project.get_funding_sources(),
            'active_tab': self.request.GET.get('tab', 'settings')
        })
        return context


class ProjectSettingsUpdateView(LoginRequiredMixin, View):
    def post(self, request, project_uuid):
        project = get_object_or_404(Project, uuid=project_uuid)

        if not project.can_user_edit(request.user):
            messages.error(request, "You don't have permission to edit this project.")
            return redirect('project:settings', project_uuid=project_uuid)

        title = request.POST.get('title')
        status = request.POST.get('status')
        description = request.POST.get('description', '')

        if title and status:
            project.title = title
            project.status = status
            project.description = description
            project._current_user = request.user
            project.save()

            messages.success(request, 'Project settings updated successfully.')
        else:
            messages.error(request, 'Invalid form data.')

        return redirect('project:settings', project_uuid=project_uuid)


class ProjectFundingCreateView(LoginRequiredMixin, CreateView):
    model = ProjectFunding
    form_class = ProjectFundingForm
    template_name = 'dashboard/project/funding_create.html'

    def get_project(self):
        return get_object_or_404(Project, uuid=self.kwargs['project_uuid'])

    def form_valid(self, form):
        if not self.get_project().can_user_edit(self.request.user):
            messages.error(self.request, "You don't have permission to add funding.")
            return redirect('project:settings', project_uuid=self.kwargs['project_uuid'])

        funding = form.save(commit=False)
        funding.project = self.get_project()
        funding._current_user = self.request.user

        try:
            funding.clean()
            funding.save()
            messages.success(self.request, 'Funding added successfully.')
            return redirect('project:settings', project_uuid=self.kwargs['project_uuid'])
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context.update({
            'project': project,
            'current_funding': project.get_funding_sources(),
        })
        return context

    def get_success_url(self):
        return reverse_lazy('project:settings', kwargs={'project_uuid': self.kwargs['project_uuid']})


class ProjectLogsView(LoginRequiredMixin, View):
    def get(self, request, project_uuid):
        project = get_object_or_404(Project, uuid=project_uuid)
        page = request.GET.get('page', 1)

        logs = project.activity_logs.select_related('actor').order_by('-timestamp')
        paginator = Paginator(logs, 20)
        page_obj = paginator.get_page(page)

        logs_data = []
        for log in page_obj:
            logs_data.append({
                'action': log.get_action_type_display(),
                'user': log.actor.get_full_name(),
                'description': log.description,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'changes': log.changes
            })

        return JsonResponse({
            'logs': logs_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages
        })


@method_decorator(require_POST, name='dispatch')
class UpdateMemberRoleView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ProjectMember
    fields = ['role']
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.project = get_object_or_404(Project, uuid=kwargs['project_uuid'])

    def test_func(self):
        return self.request.user == self.project.created_by or \
            self.project.projectmember_set.filter(
                user=self.request.user,
                role__in=['owner', 'manager']
            ).exists()

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return JsonResponse({
                'success': True,
                'role': self.object.get_role_display()
            })
        return response

@method_decorator(require_POST, name='dispatch')
class RemoveMemberView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ProjectMember

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.project = get_object_or_404(Project, uuid=kwargs['project_uuid'])
        self.object = get_object_or_404(ProjectMember,
                                        project=self.project,
                                        id=kwargs['member_id']
                                        )

    def test_func(self):
        return self.request.user == self.project.created_by or \
            self.project.projectmember_set.filter(
                user=self.request.user,
                role__in=['owner', 'manager']
            ).exists()

    def get_success_url(self):
        return reverse_lazy('project:team', kwargs={'project_uuid': self.project.uuid})

@method_decorator(csrf_protect, name='dispatch')
class TaskUpdateStatusView(LoginRequiredMixin, PermissionMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            task = get_object_or_404(Task,
                                     project__uuid=kwargs['project_uuid'],
                                     code=kwargs['code']
                                     )

            data = json.loads(request.body)
            new_status = data.get('status')

            print(f"Received status update: {new_status} for task {task.code}")  # Debug log

            # Make sure this matches your Task model's status choices
            valid_statuses = dict(Task._meta.get_field('status').choices)
            if new_status not in valid_statuses:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid status: {new_status}. Valid statuses are: {list(valid_statuses.keys())}'
                })

            task.status = new_status
            task._current_user = request.user
            task.save()

            return JsonResponse({
                'success': True,
                'message': f'Task status updated to {new_status}'
            })

        except Exception as e:
            print(f"Error updating task status: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def ProjectSettings(request):
    return render(request, 'dashboard/project/settings.html')