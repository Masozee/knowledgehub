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

class Project(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects'
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='project_memberships'
    )
    public_project = models.BooleanField(default=False)

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

class Task(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    objects = TaskManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.code}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Task.objects.generate_unique_code()
        super().save(*args, **kwargs)

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

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role} ({self.project.title})"

class ProjectGrant(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_grants')
    grant = models.OneToOneField('finance.Grant', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    submission_deadline = models.DateField()
    requirements = models.TextField()
    reporting_frequency = models.CharField(max_length=50)
    journal_entries = GenericRelation('finance.JournalEntry')
    document_proofs = GenericRelation('finance.DocumentProof')

    def __str__(self):
        return f"{self.project.title} - {self.grant.name}"

class GrantReport(models.Model):
    project_grant = models.ForeignKey(ProjectGrant, on_delete=models.CASCADE, related_name='reports')
    report_date = models.DateField()
    narrative = models.TextField()
    financial_report = models.FileField(
        upload_to='grant_reports/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'xlsx', 'docx'])]
    )
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approved = models.BooleanField(default=False)
    expenses = GenericRelation('finance.GrantExpense')
    document_proofs = GenericRelation('finance.DocumentProof')

class Publication(models.Model):
    PUBLICATION_TYPES = [
        ('journal', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('report', 'Technical Report'),
        ('book', 'Book'),
        ('chapter', 'Book Chapter'),
    ]

    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='publications')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='publications')
    publication_type = models.CharField(max_length=20, choices=PUBLICATION_TYPES)
    publisher = models.CharField(max_length=255)
    publication_date = models.DateField()
    doi = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    citation = models.TextField()
    abstract = models.TextField()
    pos_allocation = models.ForeignKey('finance.PosAllocation', on_delete=models.SET_NULL, null=True, blank=True)
    expenses = GenericRelation('finance.PosExpense')
    document_proofs = GenericRelation('finance.DocumentProof')

class ResearchData(models.Model):
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
    pos_allocation = models.ForeignKey('finance.PosAllocation', on_delete=models.SET_NULL, null=True, blank=True)
    expenses = GenericRelation('finance.PosExpense')
    document_proofs = GenericRelation('finance.DocumentProof')

class Event(models.Model):
    EVENT_TYPES = [
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('training', 'Training'),
        ('outreach', 'Outreach Event'),
    ]

    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='events')
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    target_audience = models.CharField(max_length=255)
    expected_participants = models.PositiveIntegerField()
    actual_participants = models.PositiveIntegerField(null=True, blank=True)
    pos_allocation = models.ForeignKey('finance.PosAllocation', on_delete=models.SET_NULL, null=True)
    expenses = GenericRelation('finance.PosExpense')
    document_proofs = GenericRelation('finance.DocumentProof')
    organizers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='organized_events')

    class Meta:
        verbose_name = 'Calendar Project'
        verbose_name_plural = 'Calendar Projects'

class Progress(models.Model):
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
    document_proofs = GenericRelation('finance.DocumentProof')

    def __str__(self):
        return f"{self.project.title} - {self.title}"

    class Meta:
        ordering = ['due_date', 'title']