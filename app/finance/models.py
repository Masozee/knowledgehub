from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

class MoneyField(models.DecimalField):
    """Custom field for monetary values"""
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

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)

    class Meta:
        verbose_name_plural = 'Currencies'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

class ExchangeRate(models.Model):
    from_currency = models.ForeignKey(Currency, related_name='from_rates', on_delete=models.CASCADE)
    to_currency = models.ForeignKey(Currency, related_name='to_rates', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('from_currency', 'to_currency', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.from_currency.code} to {self.to_currency.code}: {self.rate} on {self.date}"

    def clean(self):
        if self.from_currency == self.to_currency:
            raise ValidationError("From currency and To currency cannot be the same")

class DocumentProof(models.Model):
    file = models.FileField(upload_to='expense_proofs/')
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"Document proof for {self.content_object} uploaded on {self.upload_date}"

class JournalEntry(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    debit_account = models.CharField(max_length=100)
    credit_account = models.CharField(max_length=100)
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = 'Journal entries'
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.description} ({self.amount})"

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
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    document_proofs = GenericRelation(DocumentProof)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.amount})"

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")

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
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)
    document_proofs = GenericRelation(DocumentProof)

    class Meta:
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"Budget {self.fiscal_year} ({self.get_total_amount():,.2f})"

    def get_total_amount(self):
        return self.initial_amount + self.additional_amount

    def get_allocated_amount(self):
        return sum(allocation.amount for allocation in self.allocations.all())

    def get_balance(self):
        return self.get_total_amount() - self.get_allocated_amount()

    def get_pos_balance(self):
        pos_allocated = sum(allocation.amount for allocation in self.pos_allocations.all())
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

    class Meta:
        ordering = ['category']

    def get_currency_symbol(self):
        """Helper method to safely get currency symbol with fallback"""
        try:
            if self.budget and self.budget.currency:
                return getattr(self.budget.currency, 'symbol', 'Rp')
        except AttributeError:
            pass
        return '$'  # Default fallback symbol

    def __str__(self):
        try:
            symbol = self.get_currency_symbol()
            fiscal_year = self.budget.fiscal_year if self.budget else 'Unknown'
            return f"{fiscal_year} - {self.category} ({symbol}{self.amount})"
        except AttributeError:
            return f"Budget Allocation - {self.category}"

    def clean(self):
        """Validate the model before saving"""
        if not self.budget:
            raise ValidationError({'budget': 'Budget is required'})

        if not self.amount:
            raise ValidationError({'amount': 'Amount is required'})

    def save(self, *args, **kwargs):
        self.clean()  # Run validation before saving

        try:
            if self.pk:
                old_allocation = BudgetAllocation.objects.get(pk=self.pk)
                if old_allocation:
                    amount_difference = self.amount - old_allocation.amount
                else:
                    amount_difference = self.amount
            else:
                amount_difference = self.amount

            if self.budget:
                current_balance = self.budget.get_balance()
                if amount_difference > current_balance:
                    needed_additional = amount_difference - current_balance
                    self.budget.additional_amount += needed_additional
                    self.budget.save()

            super().save(*args, **kwargs)
        except Exception as e:
            # You might want to log this error
            raise ValidationError(f"Error saving budget allocation: {str(e)}")

    @property
    def formatted_amount(self):
        """Property to safely format the amount with currency symbol"""
        try:
            symbol = self.get_currency_symbol()
            return f"{symbol}{self.amount:,.2f}"
        except (AttributeError, TypeError):
            return str(self.amount)

class PosAllocation(models.Model):
    name = models.CharField(max_length=255)
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='pos_allocations', null=True, blank=True)
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='pos_allocations', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    document_proofs = GenericRelation(DocumentProof)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.amount})"

    def clean(self):
        if self.budget and self.grant:
            raise ValidationError("A POS allocation must be associated with either a budget or a grant, not both.")
        if not self.budget and not self.grant:
            raise ValidationError("A POS allocation must be associated with either a budget or a grant.")

class Expense(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)
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

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.grant.name} - {self.description} ({self.amount})"

    def clean(self):
        super().clean()
        if self.grant.currency != self.currency:
            raise ValidationError("Expense currency must match grant currency")

class PosExpense(Expense):
    pos_allocation = models.ForeignKey(PosAllocation, on_delete=models.CASCADE, related_name='expenses')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.pos_allocation.name} - {self.description} ({self.amount})"

    def clean(self):
        super().clean()
        if self.pos_allocation.currency != self.currency:
            raise ValidationError("Expense currency must match POS allocation currency")