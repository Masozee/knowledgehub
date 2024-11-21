from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Prefetch
from django.shortcuts import redirect
from django.utils import timezone
from app.project.models import *
from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower, Substr, Concat
from django.db.models import CharField, Count, Q, Prefetch
from django.db import transaction
from django.contrib import messages
from formtools.wizard.views import SessionWizardView
from django.urls import reverse_lazy
from .forms import *
from django.core.exceptions import PermissionDenied


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
        return Project.objects.select_related('created_by') \
            .prefetch_related(
            'team_members',
            'progress_items',
            'publications',
            'research_data',
            'events',
            'project_grants',
            'project_grants__grant',
            'project_grants__reports'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Get team members with roles
        team_members = ProjectMember.objects.filter(project=project) \
            .select_related('user') \
            .order_by('role', 'joined_at')

        # Get progress statistics
        progress_stats = Progress.objects.filter(project=project) \
            .aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status=100)),
            in_progress=Count('id', filter=Q(status__gt=0, status__lt=100)),
            not_started=Count('id', filter=Q(status=0))
        )

        # Calculate overall progress
        total_progress = progress_stats['total']
        if total_progress > 0:
            overall_progress = (progress_stats['completed'] / total_progress) * 100
        else:
            overall_progress = 0

        # Get publication statistics
        publication_stats = {
            'total': project.publications.count(),
            'by_type': project.publications.values('publication_type') \
                .annotate(count=Count('id'))
        }

        # Get research data statistics
        research_data_stats = {
            'total': project.research_data.count(),
            'by_type': project.research_data.values('data_type') \
                .annotate(count=Count('id'))
        }

        # Get event statistics
        event_stats = {
            'total': project.events.count(),
            'upcoming': project.events.filter(date__gt=timezone.now()).count(),
            'by_type': project.events.values('event_type') \
                .annotate(count=Count('id'))
        }

        # Get grant information
        grants = project.project_grants.select_related('grant') \
            .prefetch_related('reports') \
            .order_by('-grant__start_date')

        context.update({
            'team_members': team_members,
            'progress_items': project.progress_items.order_by('due_date'),
            'progress_stats': progress_stats,
            'overall_progress': overall_progress,
            'publications': project.publications.order_by('-publication_date'),
            'publication_stats': publication_stats,
            'research_data': project.research_data.order_by('-collection_date'),
            'research_data_stats': research_data_stats,
            'events': project.events.order_by('date'),
            'event_stats': event_stats,
            'grants': grants,
            'member_roles': ProjectMember._meta.get_field('role').choices,
            'progress_types': Progress.PROGRESS_TYPES,
            'can_edit': self.request.user == project.created_by or \
                        project.projectmember_set.filter(
                            user=self.request.user,
                            role__in=['owner', 'manager']
                        ).exists()
        })
        return context

    def post(self, request, *args, **kwargs):
        try:
            # Project creation code...
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': project.uuid,
                    'redirect_url': reverse('project:project_list')  # Updated URL name
                })
            return redirect('project:project_list')  # Updated URL name
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            return redirect('project:project_list')  # Updated URL name

    @require_POST
    def mark_project_complete(request, uuid):
        try:
            # Project completion code...
            return JsonResponse({
                'success': True,
                'message': 'Project marked as complete successfully',
                'redirect_url': reverse('project:project_list')  # Added redirect URL
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class ProjectCreateView(LoginRequiredMixin, CreateView):
    template_name = 'dashboard/project/create.html'
    form_class = ProjectCreateForm
    success_url = reverse_lazy('project:project_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Project created successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
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
