from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import (
    Grant, Budget, PosAllocation, GrantExpense,
    PosExpense, JournalEntry, BudgetAllocation
)

@receiver(post_save, sender=Grant)
def create_default_pos_allocation(sender, instance, created, **kwargs):
    """Create a default POS allocation when a new grant is created"""
    if created:
        PosAllocation.objects.create(
            name=f"Default allocation for {instance.name}",
            amount=instance.amount,
            currency=instance.currency,
            grant=instance
        )

@receiver(post_save, sender=Budget)
def create_default_budget_allocation(sender, instance, created, **kwargs):
    """Create a default budget allocation when a new budget is created"""
    if created:
        BudgetAllocation.objects.create(
            budget=instance,
            category="General",
            amount=instance.initial_amount
        )

@receiver(post_save, sender=GrantExpense)
def create_grant_expense_journal_entry(sender, instance, created, **kwargs):
    """Create a journal entry when a grant expense is recorded"""
    if created:
        JournalEntry.objects.create(
            date=instance.date,
            description=f"Grant expense: {instance.description}",
            debit_account="Grant Expenses",
            credit_account="Cash/Bank",
            amount=instance.amount,
            currency=instance.currency,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=PosExpense)
def create_pos_expense_journal_entry(sender, instance, created, **kwargs):
    """Create a journal entry when a POS expense is recorded"""
    if created:
        JournalEntry.objects.create(
            date=instance.date,
            description=f"POS expense: {instance.description}",
            debit_account=instance.pos_allocation.name,
            credit_account="Cash/Bank",
            amount=instance.amount,
            currency=instance.currency,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

# Connect signals in apps.py or __init__.py
default_app_config = 'finance.apps.FinanceConfig'