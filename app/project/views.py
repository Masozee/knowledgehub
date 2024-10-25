from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['title', 'description', 'start_date', 'end_date', 'status']
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Add team members
        team_members = self.request.POST.getlist('team_members')
        if team_members:
            for user_id in team_members:
                ProjectMember.objects.create(
                    project=self.object,
                    user_id=user_id,
                    role='member'
                )

        if self.request.is_ajax():
            return JsonResponse({'success': True, 'id': self.object.uuid})
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = get_user_model().objects.exclude(id=self.request.user.id)
        return context


@require_POST
def mark_project_complete(request, uuid):
    try:
        project = Project.objects.get(uuid=uuid)
        project.status = 'completed'
        project.save()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        queryset = queryset.select_related('created_by').prefetch_related(
            'team_members',
            'task_set',
            'projectmember_set__user'
        )

        return super().get_object(queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Get all tasks
        tasks = project.task_set.select_related('assigned_to')

        # Task statistics
        task_stats = {
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'pending': tasks.filter(status='pending').count(),
            'overdue': tasks.filter(
                due_date__lt=timezone.now().date(),
                status__in=['pending', 'in_progress']
            ).count()
        }

        # Recent activities
        recent_tasks = tasks.order_by('-updated_at')[:5]

        # Team members with their tasks
        team_members = project.projectmember_set.select_related('user').prefetch_related('user__assigned_tasks')

        team_stats = []
        for member in team_members:
            member_tasks = tasks.filter(assigned_to=member.user)
            team_stats.append({
                'member': member,
                'total_tasks': member_tasks.count(),
                'completed_tasks': member_tasks.filter(status='completed').count(),
                'in_progress_tasks': member_tasks.filter(status='in_progress').count(),
                'pending_tasks': member_tasks.filter(status='pending').count(),
            })

        context.update({
            'task_stats': task_stats,
            'recent_tasks': recent_tasks,
            'team_stats': team_stats,
            'can_edit': self.request.user == project.created_by or
                        project.projectmember_set.filter(
                            user=self.request.user,
                            role__in=['owner', 'manager']
                        ).exists(),
        })

        return context