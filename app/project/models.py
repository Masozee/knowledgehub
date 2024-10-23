from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Project(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.ForeignKey('finance.Budget', on_delete=models.SET_NULL, null=True, related_name='projects')
    currency = models.ForeignKey('finance.Currency', on_delete=models.PROTECT, null=True)
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_projects'
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='project_assignments'
    )
    journal_entries = GenericRelation('finance.JournalEntry')
    document_proofs = GenericRelation('finance.DocumentProof')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProjectMember(models.Model):
    ROLE_CHOICES = [
        ('researcher', 'Researcher'),
        ('coordinator', 'Coordinator'),
        ('analyst', 'Analyst'),
        ('volunteer', 'Volunteer'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    join_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    time_commitment = models.PositiveIntegerField(help_text="Hours per week")
    pos_allocation = models.ForeignKey('finance.PosAllocation', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ['project', 'member']

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