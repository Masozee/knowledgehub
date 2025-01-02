from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class MoneyField(models.DecimalField):
    """Custom field for monetary values with standard non-profit accounting precision"""

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = kwargs.get('max_digits', 15)  # Increased for large grants
        kwargs['decimal_places'] = kwargs.get('decimal_places', 2)
        super().__init__(*args, **kwargs)


class Currency(models.Model):
    """Currency model with standard ISO codes"""
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)

    class Meta:
        verbose_name_plural = 'Currencies'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class FiscalYear(models.Model):
    """Fiscal Year configuration for the organization"""
    year = models.IntegerField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"FY {self.year}"

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")


class SupportingDocument(models.Model):
    """Enhanced document proof model for better audit trail"""
    DOCUMENT_TYPES = [
        ('INVOICE', 'Invoice'),
        ('RECEIPT', 'Receipt'),
        ('CONTRACT', 'Contract'),
        ('REPORT', 'Financial Report'),
        ('OTHER', 'Other Documentation')
    ]

    file = models.FileField(upload_to='financial_documents/%Y/%m/')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=50, blank=True)
    document_date = models.DateField()
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-document_date']
        indexes = [
            models.Index(fields=['document_type', 'document_date']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_number} ({self.document_date})"


class FundingSource(models.Model):
    """Abstract base class for all funding sources"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    documents = GenericRelation(SupportingDocument)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_balance(self):
        """Must be implemented by subclasses"""
        raise NotImplementedError

    def to_base_currency(self, amount, date=None):
        """Convert amount to organization's base currency"""
        if not date:
            date = timezone.now().date()

        if self.currency.code == settings.BASE_CURRENCY:
            return amount

        try:
            rate = ExchangeRate.objects.get(
                from_currency=self.currency,
                to_currency=Currency.objects.get(code=settings.BASE_CURRENCY),
                date=date
            )
            return amount * rate.rate
        except ExchangeRate.DoesNotExist:
            raise ValidationError(
                f"Exchange rate not found for {self.currency.code} to {settings.BASE_CURRENCY} on {date}")


class Grant(FundingSource):
    """Enhanced Grant model for donor funding"""
    GRANT_TYPES = [
        ('RESTRICTED', 'Restricted'),
        ('UNRESTRICTED', 'Unrestricted'),
        ('PROJECT', 'Project-Based'),
        ('PROGRAM', 'Program-Based'),
    ]

    grant_type = models.CharField(max_length=20, choices=GRANT_TYPES)
    donor = models.ForeignKey('Donor', on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=50, unique=True)
    amount = MoneyField()
    start_date = models.DateField()
    end_date = models.DateField()
    reporting_frequency = models.CharField(max_length=20, choices=[
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('SEMI_ANNUAL', 'Semi-Annual'),
        ('ANNUAL', 'Annual')
    ])

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['grant_type', 'start_date']),
            models.Index(fields=['donor', 'reference_number']),
        ]

    def get_balance(self):
        """Calculate available balance"""
        # Get approved project fundings using this grant
        allocated = self.funded_projects.filter(
            status='APPROVED'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return self.amount - allocated

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class Budget(FundingSource):
    """Enhanced Budget model for organizational funds"""
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT)
    initial_amount = MoneyField()
    revised_amount = MoneyField(default=0)

    BUDGET_TYPES = [
        ('OPERATIONAL', 'Operational'),
        ('CAPITAL', 'Capital'),
        ('PROJECT', 'Project'),
        ('EMERGENCY', 'Emergency Fund')
    ]
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES)

    class Meta:
        ordering = ['-fiscal_year']
        unique_together = ['fiscal_year', 'budget_type']

    def get_total_budget(self):
        return self.initial_amount + self.revised_amount

    def get_balance(self):
        allocated = self.allocations.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return self.get_total_budget() - allocated


class BudgetLine(models.Model):
    """Budget allocation model with cost centers"""
    budget = models.ForeignKey(Budget, related_name='allocations', on_delete=models.PROTECT)
    cost_center = models.ForeignKey('CostCenter', on_delete=models.PROTECT)
    amount = MoneyField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['cost_center']
        unique_together = ['budget', 'cost_center']

    def __str__(self):
        return f"{self.cost_center} - {self.budget.fiscal_year}"


class CostCenter(models.Model):
    """Cost Center for tracking expenses across different organizational units"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Expense(models.Model):
    """Enhanced expense tracking with approval workflow"""
    EXPENSE_TYPES = [
        ('DIRECT', 'Direct Cost'),
        ('INDIRECT', 'Indirect Cost'),
        ('OVERHEAD', 'Overhead'),
    ]

    EXPENSE_STATUS = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid')
    ]

    date = models.DateField()
    description = models.TextField()
    amount = MoneyField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.PROTECT)

    # Funding source - either grant or budget
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    funding_source = GenericForeignKey('content_type', 'object_id')

    status = models.CharField(max_length=20, choices=EXPENSE_STATUS, default='DRAFT')
    documents = GenericRelation(SupportingDocument)

    # Approval workflow
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submitted_expenses', on_delete=models.PROTECT)
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='approved_expenses', null=True, blank=True,
                                    on_delete=models.PROTECT)
    approved_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['status', 'date']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.date} - {self.description} ({self.amount} {self.currency.code})"

    def clean(self):
        if self.status == 'APPROVED' and not self.approved_by:
            raise ValidationError("Approved expenses must have an approver")

        if self.status == 'SUBMITTED' and not self.submitted_date:
            raise ValidationError("Submitted expenses must have a submission date")


class Donor(models.Model):
    """Donor organization information"""
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField()
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ExchangeRate(models.Model):
    """Daily exchange rates"""
    from_currency = models.ForeignKey(Currency, related_name='from_rates', on_delete=models.CASCADE)
    to_currency = models.ForeignKey(Currency, related_name='to_rates', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    date = models.DateField()

    class Meta:
        unique_together = ('from_currency', 'to_currency', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'from_currency', 'to_currency']),
        ]

    def __str__(self):
        return f"{self.date}: {self.from_currency.code}/{self.to_currency.code} = {self.rate}"