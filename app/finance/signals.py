from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grant, GrantExpense, BudgetAllocation, PosAllocation, PosExpense, JournalEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

@receiver(post_save, sender=Grant)
def create_grant_journal_entry(sender, instance, created, **kwargs):
    if created:
        JournalEntry.objects.create(
            date=instance.start_date,
            description=f"Grant received: {instance.name}",
            debit_account="Bank",
            credit_account="Grant Revenue",
            amount=instance.amount,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=GrantExpense)
def create_grant_expense_journal_entry(sender, instance, created, **kwargs):
    if created:
        JournalEntry.objects.create(
            date=instance.date,
            description=f"Grant expense: {instance.description} for {instance.grant.name}",
            debit_account="Grant Expenses",
            credit_account="Bank",
            amount=instance.amount,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=BudgetAllocation)
def create_budget_allocation_journal_entry(sender, instance, created, **kwargs):
    if created:
        JournalEntry.objects.create(
            date=timezone.now(),
            description=f"Budget allocation: {instance.category} for FY {instance.budget.fiscal_year}",
            debit_account="Budget Allocations",
            credit_account="Available Budget",
            amount=instance.amount,
            related_object=instance
        )

@receiver(post_save, sender=PosAllocation)
def create_pos_allocation_journal_entry(sender, instance, created, **kwargs):
    if created:
        account_type = "Budget" if instance.budget else "Grant"
        JournalEntry.objects.create(
            date=timezone.now(),
            description=f"POS Allocation: {instance.name} for {account_type} {instance.budget or instance.grant}",
            debit_account=f"{account_type} POS Allocations",
            credit_account=f"Available {account_type}",
            amount=instance.amount,
            related_object=instance
        )

@receiver(post_save, sender=PosExpense)
def create_pos_expense_journal_entry(sender, instance, created, **kwargs):
    if created:
        account_type = "Budget" if instance.pos_allocation.budget else "Grant"
        JournalEntry.objects.create(
            date=instance.date,
            description=f"POS Expense: {instance.description} for {instance.pos_allocation.name}",
            debit_account=f"{account_type} POS Expenses",
            credit_account="Bank",
            amount=instance.amount,
            related_object=instance
        )