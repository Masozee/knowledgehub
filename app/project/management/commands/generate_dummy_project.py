# project/management/commands/generate_project_dummy_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.project.models import (
    Project, Task, ProjectMember, ResearchData, ProjectFunding, ProjectBudgetLine, ProjectExpense, Progress, ActivityLog
)
from app.finance.models import Grant, Budget, CostCenter
import random
import uuid
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates dummy data for Project and related models'

    def handle(self, *args, **kwargs):
        # Create users if they don't exist
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                email=f"user{i}@example.com",
                defaults={
                    'first_name': f"User{i}",
                    'last_name': "Doe",
                    'is_email_verified': True
                }
            )
            users.append(user)

        # Create projects
        projects = []
        for i in range(3):
            project = Project.objects.create(
                title=f"Project {i + 1}",
                description=f"Description for Project {i + 1}",
                status=random.choice(['planning', 'active', 'on_hold', 'completed', 'cancelled']),
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=random.randint(30, 365)),
                public_project=random.choice([True, False]),
                created_by=random.choice(users)
            )
            projects.append(project)

        # Create project members
        for project in projects:
            for user in users:
                ProjectMember.objects.create(
                    project=project,
                    user=user,
                    role=random.choice(['owner', 'manager', 'member', 'viewer', 'outreach'])
                )

        # Create tasks
        for project in projects:
            for i in range(5):
                Task.objects.create(
                    project=project,
                    title=f"Task {i + 1} for {project.title}",
                    description=f"Description for Task {i + 1}",
                    status=random.choice(['pending', 'in_progress', 'completed', 'cancelled']),
                    assigned_to=random.choice(users),
                    due_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                    created_by=random.choice(users)
                )

        # Create research data
        for project in projects:
            for i in range(2):
                ResearchData.objects.create(
                    project=project,
                    title=f"Research Data {i + 1} for {project.title}",
                    data_type=random.choice(['survey', 'interview', 'observation', 'experimental', 'secondary']),
                    collection_date=timezone.now().date(),
                    description=f"Description for Research Data {i + 1}",
                    methodology="Sample methodology",
                    storage_location="/path/to/storage",
                    file="research_data/sample_file.pdf",
                    responsible_person=random.choice(users)
                )

        # Create grants and budgets
        grants = []
        budgets = []
        for i in range(2):
            grants.append(Grant.objects.create(
                name=f"Grant {i + 1}",
                amount=random.randint(10000, 50000),
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=random.randint(180, 365))
            ))
            budgets.append(Budget.objects.create(
                name=f"Budget {i + 1}",
                amount=random.randint(10000, 50000),
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=random.randint(180, 365))
            ))

        # Create project funding
        for project in projects:
            for i in range(2):
                ProjectFunding.objects.create(
                    project=project,
                    grant=random.choice(grants) if i % 2 == 0 else None,
                    budget=random.choice(budgets) if i % 2 != 0 else None,
                    amount=random.randint(1000, 10000),
                    status=random.choice(['DRAFT', 'PROPOSED', 'APPROVED', 'ACTIVE', 'CLOSED', 'CANCELLED']),
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timedelta(days=random.randint(30, 180))
                )

        # Create project budget lines
        for project in projects:
            for funding in project.funding_sources.all():
                for i in range(3):
                    ProjectBudgetLine.objects.create(
                        project=project,
                        project_funding=funding,
                        category=random.choice(['PERSONNEL', 'EQUIPMENT', 'SUPPLIES', 'TRAVEL', 'SERVICES', 'OTHER']),
                        description=f"Budget Line {i + 1} for {project.title}",
                        amount=random.randint(100, 1000),
                        timeline=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                        responsible_person=random.choice(users)
                    )

        # Create project expenses
        for project in projects:
            for budget_line in project.budget_lines.all():
                for i in range(2):
                    ProjectExpense.objects.create(
                        project=project,
                        budget_line=budget_line,
                        description=f"Expense {i + 1} for {budget_line.description}",
                        amount=random.randint(10, 100),
                        expense_date=timezone.now().date(),
                        status=random.choice(['DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'PAID']),
                        submitted_by=random.choice(users)
                    )

        # Create progress items
        for project in projects:
            for i in range(3):
                Progress.objects.create(
                    project=project,
                    title=f"Progress {i + 1} for {project.title}",
                    progress_type=random.choice(['milestone', 'deliverable', 'objective']),
                    description=f"Description for Progress {i + 1}",
                    due_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                    completion_date=timezone.now().date() if random.choice([True, False]) else None,
                    status=random.randint(0, 100),
                    responsible_person=random.choice(users)
                )

        # Create activity logs
        for project in projects:
            for i in range(5):
                ActivityLog.objects.create(
                    actor=random.choice(users),
                    action_type=random.choice(['create', 'update', 'delete', 'status_change', 'assignment']),
                    content_object=random.choice(project.tasks.all()),
                    project=project,
                    description=f"Activity Log {i + 1} for {project.title}",
                    changes={"sample_field": "sample_value"}
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data for Project and related models!'))