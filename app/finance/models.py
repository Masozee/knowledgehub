# In finance/models.py

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class JournalEntry(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    debit_account = models.CharField(max_length=100)
    credit_account = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Generic Foreign Key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.date} - {self.description} (${self.amount})"


class Grant(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

    def get_balance(self):
        total_expenses = sum(expense.amount for expense in self.expenses.all())
        return self.amount - total_expenses

    def get_pos_balance(self):
        total_allocated = sum(allocation.amount for allocation in self.pos_allocations.all())
        return self.amount - total_allocated

class Budget(models.Model):
    fiscal_year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Budget {self.fiscal_year}"

    def get_balance(self):
        total_allocated = sum(allocation.amount for allocation in self.allocations.all())
        return self.total_amount - total_allocated

    def get_pos_balance(self):
        total_allocated = sum(allocation.amount for allocation in self.pos_allocations.all())
        return self.total_amount - total_allocated

class BudgetAllocation(models.Model):
    budget = models.ForeignKey(Budget, related_name='allocations', on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.budget.fiscal_year} - {self.category} (${self.amount})"

class PosAllocation(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='pos_allocations', null=True, blank=True)
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='pos_allocations', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - ${self.amount}"

    def clean(self):
        if self.budget and self.grant:
            raise ValidationError("A POS allocation must be associated with either a budget or a grant, not both.")
        if not self.budget and not self.grant:
            raise ValidationError("A POS allocation must be associated with either a budget or a grant.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_balance(self):
        total_expenses = sum(expense.amount for expense in self.expenses.all())
        return self.amount - total_expenses

class DocumentProof(models.Model):
    file = models.FileField(upload_to='expense_proofs/')
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Document proof uploaded on {self.upload_date}"

    def get_related_object_str(self):
        return str(self.content_object)

class Expense(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    document_proof = models.ForeignKey(DocumentProof, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

class GrantExpense(Expense):
    grant = models.ForeignKey(Grant, related_name='expenses', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.grant.name} - {self.description} (${self.amount})"

class PosExpense(Expense):
    pos_allocation = models.ForeignKey(PosAllocation, on_delete=models.CASCADE, related_name='expenses')

    def __str__(self):
        return f"{self.pos_allocation.name} - {self.description} (${self.amount})"


