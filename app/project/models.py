import random
import string
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import uuid
from django.urls import reverse
from django.db.models import Count, Q
from model_utils import FieldTracker
from app.project.mixins import AuditModelMixin
from django.contrib.contenttypes.fields import GenericRelation
from app.finance.models import *

class TaskManager(models.Manager):
    def generate_unique_code(self):
        """Generate a unique 6-character code with mix of numbers and letters"""
        length = 6
        while True:
            # Generate 3 letters and 3 numbers
            letters = ''.join(random.choices(string.ascii_uppercase, k=3))
            numbers = ''.join(random.choices(string.digits, k=3))

            # Combine and shuffle them
            code = list(letters + numbers)
            random.shuffle(code)
            code = ''.join(code)

            # Check if this code already exists
            if not self.filter(code=code).exists():
                return code

class Project(AuditModelMixin, models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=(
            ('planning', 'Planning'),
            ('active', 'Active'),
            ('on_hold', 'On Hold'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ),
        default='planning'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        through_fields=('project', 'user'),
    )
    public_project = models.BooleanField(default=False)
    tracker = FieldTracker()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project:project_detail', kwargs={'uuid': self.uuid})

    @property
    def status_color(self):
        """Return Bootstrap color class based on status"""
        color_map = {
            'planning': 'info',
            'active': 'success',
            'on_hold': 'warning',
            'completed': 'primary',
            'cancelled': 'danger',
        }
        return color_map.get(self.status, 'secondary')

    @property
    def progress(self):
        """Calculate project progress based on task completion"""
        try:
            # Try to get task statistics
            task_stats = self.task_set.aggregate(
                total_tasks=Count('id'),
                completed_tasks=Count('id', filter=Q(status='completed'))
            )

            total = task_stats.get('total_tasks', 0)
            completed = task_stats.get('completed_tasks', 0)

            # Calculate percentage if there are tasks
            if total > 0:
                return int((completed / total) * 100)

            # If no tasks exist, base progress on status
            status_progress = {
                'planning': 0,
                'active': 25,
                'on_hold': 50,
                'completed': 100,
                'cancelled': 0,
            }
            return status_progress.get(self.status, 0)

        except Exception:
            return 0

    def get_task_stats(self):
        """Get detailed task statistics"""
        return {
            'total': self.task_set.count(),
            'completed': self.task_set.filter(status='completed').count(),
            'in_progress': self.task_set.filter(status='in_progress').count(),
            'pending': self.task_set.filter(status='pending').count()
        }

    def can_user_edit(self, user):
        """
        Check if user can edit this project
        Returns True if user is project creator or has owner/manager role
        """
        if user == self.created_by:
            return True

        return self.projectmember_set.filter(
            user=user,
            role__in=['owner', 'manager']
        ).exists()

    @property
    def team_count(self):
        """Get the number of team members"""
        return self.team_members.count()

    @property
    def is_completed(self):
        """Check if project is completed"""
        return self.status == 'completed'

    @property
    def is_active(self):
        """Check if project is active"""
        return self.status == 'active'

    @property
    def days_left(self):
        """Calculate days left until project end date"""
        from datetime import date

        if self.end_date:
            today = date.today()
            days_remaining = (self.end_date - today).days
            return max(days_remaining, 0)  # Return 0 if end date has passed
        return None

    def get_total_budget(self):
        """Calculate total project budget across all funding sources"""
        return self.funding_sources.filter(
            status='APPROVED'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    def get_total_expenses(self):
        """Calculate total approved expenses"""
        return self.expenses.filter(
            status='APPROVED'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    def get_remaining_budget(self):
        """Calculate remaining budget"""
        return self.get_total_budget() - self.get_total_expenses()

    def get_budget_utilization(self):
        """Calculate budget utilization percentage"""
        total_budget = self.get_total_budget()
        if total_budget > 0:
            return (self.get_total_expenses() / total_budget) * 100
        return 0

    def get_funding_sources(self):
        """Get all funding sources with their details"""
        sources = []
        for funding in self.funding_sources.filter(status='APPROVED'):
            source = funding.grant or funding.budget
            sources.append({
                'type': 'Grant' if funding.grant else 'Budget',
                'name': str(source),
                'amount': funding.amount,
                'currency': source.currency.code,
                'start_date': funding.start_date,
                'end_date': funding.end_date,
                'status': funding.status
            })
        return sources

    def get_budget_breakdown(self):
        """Get budget breakdown by category"""
        return self.budget_lines.values('category').annotate(
            total=models.Sum('amount'),
            spent=models.Sum(
                'expenses__amount',
                filter=models.Q(expenses__status='APPROVED')
            )
        )

    def get_monthly_expenses(self, year=None, month=None):
        """Get monthly expense breakdown"""
        queryset = self.expenses.filter(status='APPROVED')

        if year:
            queryset = queryset.filter(expense_date__year=year)
        if month:
            queryset = queryset.filter(expense_date__month=month)

        return queryset.values(
            'budget_line__category'
        ).annotate(
            total=models.Sum('amount')
        ).order_by('budget_line__category')

    def can_add_expense(self, amount, budget_line):
        """Check if an expense can be added to a specific budget line"""
        if not budget_line:
            return False

        used_amount = budget_line.expenses.filter(
            status='APPROVED'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        return (used_amount + amount) <= budget_line.amount

    def save(self, *args, **kwargs):
        self._current_user = getattr(self, '_current_user', None)
        super().save(*args, **kwargs)

class Task(AuditModelMixin, models.Model):
    """Task model for project tasks"""
    code = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        editable=False,
        help_text="Unique 6-character task identifier"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ),
        default='pending'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    due_date = models.DateField(null=True, blank=True)
    objects = TaskManager()
    tracker = FieldTracker(fields=['status', 'assigned_to', 'title', 'description', 'due_date'])

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.code}] {self.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        skip_log = kwargs.pop('skip_log', False)  # Add skip_log parameter

        # Set current user for AuditModelMixin
        self._current_user = getattr(self, '_current_user', None)

        # Generate code for new tasks
        if not self.code:
            self.code = Task.objects.generate_unique_code()

        # Call parent save with skip_log to prevent double logging
        if is_new:
            kwargs['skip_log'] = True
        super().save(*args, **kwargs)

        # Skip the rest if we're told to skip logging
        if skip_log:
            return

        # Get the actor AFTER parent save
        actor = self._current_user or self.created_by
        if not actor:
            actor = self.project.created_by

        if is_new:
            # Log task creation
            ActivityLog.log_activity(
                actor=actor,
                action_type='create',
                content_object=self,
                project=self.project,
                description=f"Created task: {self.title}"
            )
            return  # Exit after creation log

        # Track status changes
        if self.tracker.has_changed('status'):
            ActivityLog.log_activity(
                actor=actor,
                action_type='status_change',
                content_object=self,
                project=self.project,
                description=f"Changed task status: {self.title}",
                changes={
                    'from_status': self.tracker.previous('status'),
                    'to_status': self.status
                }
            )

        # Track assignment changes
        if self.tracker.has_changed('assigned_to'):
            old_user = None
            if self.tracker.previous('assigned_to'):
                try:
                    old_user = settings.AUTH_USER_MODEL.objects.get(
                        id=self.tracker.previous('assigned_to')
                    )
                except settings.AUTH_USER_MODEL.DoesNotExist:
                    pass

            ActivityLog.log_activity(
                actor=actor,
                action_type='assignment',
                content_object=self,
                project=self.project,
                description=f"Changed task assignment: {self.title}",
                changes={
                    'from_user': str(old_user) if old_user else None,
                    'to_user': str(self.assigned_to) if self.assigned_to else None
                }
            )

        # Track other important changes
        changed_fields = []
        for field in ['title', 'description', 'due_date']:
            if self.tracker.has_changed(field):
                changed_fields.append({
                    'field': field,
                    'from': self.tracker.previous(field),
                    'to': getattr(self, field)
                })

        if changed_fields:
            ActivityLog.log_activity(
                actor=actor,
                action_type='update',
                content_object=self,
                project=self.project,
                description=f"Updated task: {self.title}",
                changes={'changed_fields': changed_fields}
            )

    # Your existing properties and methods remain the same
    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status == 'completed'

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and not self.is_completed:
            return self.due_date < timezone.now().date()
        return False

    def can_user_edit(self, user):
        """
        Check if user can edit this task
        Returns True if user has edit permission on the project
        """
        return self.project.can_user_edit(user)

    @property
    def status_color(self):
        """Return Bootstrap color class based on status"""
        color_map = {
            'pending': 'secondary',
            'in_progress': 'primary',
            'completed': 'success',
            'cancelled': 'danger',
        }
        return color_map.get(self.status, 'secondary')

    def get_absolute_url(self):
        """Get the absolute URL for the task"""
        return reverse('project:task_detail', kwargs={
            'project_uuid': self.project.uuid,
            'code': self.code
        })

    def can_user_edit(self, user):
        """Check if user can edit this task"""
        if user == self.project.created_by:
            return True
        return self.project.projectmember_set.filter(
            user=user,
            role__in=['owner', 'manager']
        ).exists()

    activity_logs = GenericRelation('ActivityLog',
                                    content_type_field='content_type',
                                    object_id_field='object_id',
                                    related_query_name='task'
                                    )

class ProjectMember(AuditModelMixin, models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_member_roles'
    )
    role = models.CharField(
        max_length=20,
        choices=(
            ('owner', 'Project Owner'),
            ('manager', 'Project Manager'),
            ('member', 'Team Member'),
            ('viewer', 'Viewer'),
            ('outreach', 'Team Outreach'),
        ),
        default='member'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role} ({self.project.title})"

class ResearchData(AuditModelMixin, models.Model):
    DATA_TYPES = [
        ('survey', 'Survey Data'),
        ('interview', 'Interview Data'),
        ('observation', 'Observation Data'),
        ('experimental', 'Experimental Data'),
        ('secondary', 'Secondary Data'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='research_data')
    title = models.CharField(max_length=255)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    collection_date = models.DateField()
    description = models.TextField()
    methodology = models.TextField()
    storage_location = models.CharField(max_length=255)
    file = models.FileField(upload_to='research_data/')
    metadata = models.JSONField()
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

class ProjectFunding(AuditModelMixin, models.Model):
    """
    Model to manage project funding from multiple sources (grants/budgets)
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PROPOSED', 'Proposed'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled')
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='funding_sources'
    )

    # Either grant or budget, not both
    grant = models.ForeignKey(
        Grant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='funded_projects'
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='funded_projects'
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Allocated amount from this funding source"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    start_date = models.DateField()
    end_date = models.DateField()

    notes = models.TextField(blank=True)
    supporting_documents = GenericRelation('finance.SupportingDocument')

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                        models.Q(grant__isnull=True, budget__isnull=False) |
                        models.Q(grant__isnull=False, budget__isnull=True)
                ),
                name='project_funding_single_source'
            )
        ]

    def clean(self):
        if self.grant and self.budget:
            raise ValidationError(
                "A project funding entry must be associated with either a grant or a budget, not both")
        if not self.grant and not self.budget:
            raise ValidationError("A project funding entry must be associated with either a grant or a budget")

        # Validate dates against project timeline
        if self.start_date < self.project.start_date:
            raise ValidationError("Funding start date cannot be before project start date")
        if self.end_date > self.project.end_date:
            raise ValidationError("Funding end date cannot be after project end date")

        # Validate amount against available funding
        funding_source = self.grant or self.budget
        if funding_source:
            available = funding_source.get_balance()
            if self.amount > available:
                raise ValidationError(f"Requested amount exceeds available funding ({available})")

    def get_funding_source(self):
        """Helper method to get the actual funding source object"""
        return self.grant or self.budget

    def get_currency(self):
        """Get the currency of the funding source"""
        source = self.get_funding_source()
        return source.currency if source else None

    def __str__(self):
        source = self.get_funding_source()
        return f"{self.project.title} - {source} ({self.amount})"

class ProjectBudgetLine(AuditModelMixin, models.Model):
    """
    Model to track detailed budget planning for project activities
    """
    CATEGORY_CHOICES = [
        ('PERSONNEL', 'Personnel Costs'),
        ('EQUIPMENT', 'Equipment'),
        ('SUPPLIES', 'Supplies'),
        ('TRAVEL', 'Travel'),
        ('SERVICES', 'Services'),
        ('OTHER', 'Other Expenses')
    ]

    project = models.ForeignKey(
        'Project',
        on_delete=models.PROTECT,
        related_name='budget_lines'
    )
    project_funding = models.ForeignKey(
        ProjectFunding,
        on_delete=models.PROTECT,
        related_name='budget_lines'
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    # Optional fields for better tracking
    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timeline = models.DateField(
        help_text="Expected date of expenditure"
    )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responsible_budget_lines'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['category', 'timeline']

    def clean(self):
        # Validate amount against project funding
        used_amount = self.project_funding.budget_lines.exclude(
            pk=self.pk
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        remaining = self.project_funding.amount - used_amount
        if self.amount > remaining:
            raise ValidationError(f"Amount exceeds remaining budget ({remaining})")

    def __str__(self):
        return f"{self.project.title} - {self.get_category_display()} ({self.amount})"

class ProjectExpense(AuditModelMixin, models.Model):
    """
    Model to track actual project expenses against budget lines
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid')
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    budget_line = models.ForeignKey(
        ProjectBudgetLine,
        on_delete=models.PROTECT,
        related_name='expenses'
    )

    description = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    expense_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    # Approval workflow
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='submitted_project_expenses'
    )
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='approved_project_expenses'
    )
    approved_date = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    supporting_documents = GenericRelation('finance.SupportingDocument')

    class Meta:
        ordering = ['-expense_date']

    def clean(self):
        # Validate amount against budget line
        used_amount = self.budget_line.expenses.exclude(
            pk=self.pk
        ).filter(
            status='APPROVED'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        remaining = self.budget_line.amount - used_amount
        if self.amount > remaining:
            raise ValidationError(f"Amount exceeds remaining budget line amount ({remaining})")

    def __str__(self):
        return f"{self.project.title} - {self.description} ({self.amount})"

class Progress(AuditModelMixin, models.Model):
    PROGRESS_TYPES = [
        ('milestone', 'Milestone'),
        ('deliverable', 'Deliverable'),
        ('objective', 'Objective'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='progress_items')
    title = models.CharField(max_length=255)
    progress_type = models.CharField(max_length=20, choices=PROGRESS_TYPES)
    description = models.TextField()
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(default=0, help_text="Progress percentage (0-100)")
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    attachments = models.FileField(upload_to='progress_attachments/', null=True, blank=True)
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.project.title} - {self.title}"

    class Meta:
        ordering = ['due_date', 'title']

    def save(self, *args, **kwargs):
        self._current_user = getattr(self, '_current_user', None)
        super().save(*args, **kwargs)

class ActivityLog(AuditModelMixin, models.Model):
    """
    Model to track all activities across project-related models
    """
    ACTION_TYPES = [
        ('create', _('Created')),
        ('update', _('Updated')),
        ('delete', _('Deleted')),
        ('status_change', _('Status Changed')),
        ('assignment', _('Assignment Changed')),
        ('comment', _('Comment Added')),
        ('file_upload', _('File Uploaded')),
        ('member_add', _('Member Added')),
        ('member_remove', _('Member Removed')),
        ('submission', _('Submission Made')),
        ('completion', _('Marked as Complete')),
    ]

    # Who performed the action
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities',
        help_text=_('User who performed the action')
    )

    # Action details
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text=_('Type of action performed')
    )

    # When the action was performed
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the action occurred')
    )

    # Generic foreign key to the object being acted upon
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)  # Using CharField to handle both int and UUID
    content_object = GenericForeignKey('content_type', 'object_id')

    # Related project (for easier querying)
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text=_('Related project')
    )

    # Additional details about the action
    description = models.TextField(
        help_text=_('Detailed description of the action')
    )

    changes = models.JSONField(
        null=True,
        blank=True,
        help_text=_('JSON containing the changes made')
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['project', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.actor} {self.get_action_type_display()} {self.content_object} at {self.timestamp}"

    @classmethod
    def log_activity(cls, actor, action_type, content_object, project, description, changes=None):
        """
        Helper method to create activity logs
        """
        return cls.objects.create(
            actor=actor,
            action_type=action_type,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=str(content_object.pk),
            content_object=content_object,
            project=project,
            description=description,
            changes=changes
        )
