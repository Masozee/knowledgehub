from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.code} - {self.name}"

class ExchangeRate(models.Model):
    from_currency = models.ForeignKey(Currency, related_name='from_rates', on_delete=models.CASCADE)
    to_currency = models.ForeignKey(Currency, related_name='to_rates', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('from_currency', 'to_currency', 'date')

    def __str__(self):
        return f"{self.from_currency.code} to {self.to_currency.code}: {self.rate} on {self.date}"

class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = kwargs.get('max_digits', 12)
        kwargs['decimal_places'] = kwargs.get('decimal_places', 2)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_digits') == 12:
            del kwargs['max_digits']
        if kwargs.get('decimal_places') == 2:
            del kwargs['decimal_places']
        return name, path, args, kwargs

class JournalEntry(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    debit_account = models.CharField(max_length=100)
    credit_account = models.CharField(max_length=100)
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.date} - {self.description} ({self.currency.symbol}{self.amount})"

    def to_rupiah(self):
        if self.currency.code == 'IDR':
            return self.amount
        try:
            rate = ExchangeRate.objects.get(
                from_currency=self.currency,
                to_currency=Currency.objects.get(code='IDR'),
                date=self.date
            )
            return self.amount * rate.rate
        except ExchangeRate.DoesNotExist:
            raise ValidationError(f"Exchange rate not found for {self.currency.code} to IDR on {self.date}")

class Grant(models.Model):
    name = models.CharField(max_length=255)
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

    def get_balance(self):
        total_expenses = sum(expense.to_rupiah() for expense in self.expenses.all())
        return self.to_rupiah() - total_expenses

    def get_pos_balance(self):
        total_allocated = sum(allocation.to_rupiah() for allocation in self.pos_allocations.all())
        return self.to_rupiah() - total_allocated

    def to_rupiah(self):
        if self.currency.code == 'IDR':
            return self.amount
        try:
            rate = ExchangeRate.objects.get(
                from_currency=self.currency,
                to_currency=Currency.objects.get(code='IDR'),
                date=timezone.now().date()
            )
            return self.amount * rate.rate
        except ExchangeRate.DoesNotExist:
            raise ValidationError(f"Exchange rate not found for {self.currency.code} to IDR")

class Budget(models.Model):
    fiscal_year = models.IntegerField()
    initial_amount = MoneyField()
    additional_amount = MoneyField(default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    def __str__(self):
        return f"Budget {self.fiscal_year}"

    def get_total_amount(self):
        return self.to_rupiah(self.initial_amount) + self.to_rupiah(self.additional_amount)

    def get_allocated_amount(self):
        return sum(self.to_rupiah(allocation.amount) for allocation in self.allocations.all())

    def get_balance(self):
        return self.get_total_amount() - self.get_allocated_amount()

    def get_pos_balance(self):
        pos_allocated = sum(self.to_rupiah(allocation.amount) for allocation in self.pos_allocations.all())
        return self.get_total_amount() - pos_allocated

    def to_rupiah(self, amount):
        if self.currency.code == 'IDR':
            return amount
        try:
            rate = ExchangeRate.objects.get(
                from_currency=self.currency,
                to_currency=Currency.objects.get(code='IDR'),
                date=timezone.now().date()
            )
            return amount * rate.rate
        except ExchangeRate.DoesNotExist:
            raise ValidationError(f"Exchange rate not found for {self.currency.code} to IDR")

class BudgetAllocation(models.Model):
    budget = models.ForeignKey(Budget, related_name='allocations', on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = MoneyField()

    def __str__(self):
        return f"{self.budget.fiscal_year} - {self.category} ({self.budget.currency.symbol}{self.amount})"

    def save(self, *args, **kwargs):
        if self.pk:
            old_amount = BudgetAllocation.objects.get(pk=self.pk).amount
            amount_difference = self.amount - old_amount
        else:
            amount_difference = self.amount

        current_total = self.budget.get_total_amount()
        new_total_allocated = self.budget.get_allocated_amount() + self.budget.to_rupiah(amount_difference)

        if new_total_allocated > current_total:
            self.budget.additional_amount += self.budget.to_rupiah(new_total_allocated - current_total)
            self.budget.save()

        super().save(*args, **kwargs)

class PosAllocation(models.Model):
    name = models.CharField(max_length=255)
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='pos_allocations', null=True, blank=True)
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='pos_allocations', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.currency.symbol}{self.amount}"

    def clean(self):
        if self.budget and self.grant:
            raise ValidationError("A POS allocation must be associated with either a budget or a grant, not both.")
        if not self.budget and not self.grant:
            raise ValidationError("A POS allocation must be associated with either a budget or a grant.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.budget:
            if self.pk:
                old_amount = PosAllocation.objects.get(pk=self.pk).amount
                amount_difference = self.amount - old_amount
            else:
                amount_difference = self.amount

            current_total = self.budget.get_total_amount()
            new_total_allocated = sum(self.budget.to_rupiah(allocation.amount) for allocation in self.budget.pos_allocations.exclude(pk=self.pk)) + self.budget.to_rupiah(self.amount)

            if new_total_allocated > current_total:
                self.budget.additional_amount += self.budget.to_rupiah(new_total_allocated - current_total)
                self.budget.save()

        super().save(*args, **kwargs)

    def get_balance(self):
        total_expenses = sum(expense.to_rupiah() for expense in self.expenses.all())
        return self.to_rupiah() - total_expenses

    def to_rupiah(self):
        if self.currency.code == 'IDR':
            return self.amount
        try:
            rate = ExchangeRate.objects.get(
                from_currency=self.currency,
                to_currency=Currency.objects.get(code='IDR'),
                date=timezone.now().date()
            )
            return self.amount * rate.rate
        except ExchangeRate.DoesNotExist:
            raise ValidationError(f"Exchange rate not found for {self.currency.code} to IDR")

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
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    document_proof = models.ForeignKey(DocumentProof, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

    def to_rupiah(self):
        if self.currency.code == 'IDR':
            return self.amount
        try:
            rate = ExchangeRate.objects.get(
                from_currency=self.currency,
                to_currency=Currency.objects.get(code='IDR'),
                date=self.date
            )
            return self.amount * rate.rate
        except ExchangeRate.DoesNotExist:
            raise ValidationError(f"Exchange rate not found for {self.currency.code} to IDR on {self.date}")

class GrantExpense(Expense):
    grant = models.ForeignKey(Grant, related_name='expenses', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.grant.name} - {self.description} ({self.currency.symbol}{self.amount})"

class PosExpense(Expense):
    pos_allocation = models.ForeignKey(PosAllocation, on_delete=models.CASCADE, related_name='expenses')

    def __str__(self):
        return f"{self.pos_allocation.name} - {self.description} ({self.currency.symbol}{self.amount})"