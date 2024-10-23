from django.contrib import admin
from django.db.models import Count, Sum, F, OuterRef, Subquery, ExpressionWrapper, DecimalField
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils import timezone
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import gettext_lazy as _
import csv
from datetime import datetime, timedelta
from decimal import Decimal
from import_export.admin import ExportMixin

from .models import (
    Currency, ExchangeRate, Grant, Budget, BudgetAllocation,
    PosAllocation, DocumentProof, JournalEntry, GrantExpense,
    PosExpense
)


# Custom Filters
class CurrencyExchangeFilter(SimpleListFilter):
    title = _('exchange rate availability')
    parameter_name = 'exchange_rate'

    def lookups(self, request, model_admin):
        return (
            ('available', _('Exchange Rate Available')),
            ('missing', _('Exchange Rate Missing')),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'available':
            return queryset.filter(
                from_rates__date=today
            )
        if self.value() == 'missing':
            return queryset.exclude(
                from_rates__date=today
            )


class BudgetStatusFilter(SimpleListFilter):
    title = _('budget status')
    parameter_name = 'budget_status'

    def lookups(self, request, model_admin):
        return (
            ('over', _('Over Budget')),
            ('warning', _('Near Limit (>80%)')),
            ('ok', _('Under Budget')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'over':
            return queryset.annotate(
                usage=Sum('pos_allocations__expenses__amount') / F('initial_amount') * 100
            ).filter(usage__gt=100)
        if self.value() == 'warning':
            return queryset.annotate(
                usage=Sum('pos_allocations__expenses__amount') / F('initial_amount') * 100
            ).filter(usage__gte=80, usage__lte=100)
        if self.value() == 'ok':
            return queryset.annotate(
                usage=Sum('pos_allocations__expenses__amount') / F('initial_amount') * 100
            ).filter(usage__lt=80)


# Custom Admin Mixins
class ExportMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'

        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


# Inline Admin Classes
class DocumentProofInline(GenericTabularInline):
    model = DocumentProof
    extra = 1
    readonly_fields = ('upload_date',)
    fields = ('file', 'description', 'upload_date')
    classes = ('collapse',)


class JournalEntryInline(GenericTabularInline):
    model = JournalEntry
    extra = 0
    readonly_fields = ('date',)
    fields = ('date', 'description', 'debit_account', 'credit_account',
              'amount', 'currency')


class BudgetAllocationInline(admin.TabularInline):
    model = BudgetAllocation
    extra = 1
    fields = ('category', 'amount')


class PosAllocationInline(admin.TabularInline):
    model = PosAllocation
    extra = 1
    fields = ('name', 'amount', 'currency')


class GrantExpenseInline(admin.TabularInline):
    model = GrantExpense
    extra = 1
    fields = ('date', 'description', 'amount', 'currency', 'document_proof')


class PosExpenseInline(admin.TabularInline):
    model = PosExpense
    extra = 1
    fields = ('date', 'description', 'amount', 'currency', 'document_proof')


# Main Admin Classes
@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('code', 'name', 'symbol', 'exchange_rate_count')
    search_fields = ('code', 'name')
    ordering = ('code',)
    actions = ['export_as_csv']

    def exchange_rate_count(self, obj):
        return obj.from_rates.count()

    exchange_rate_count.short_description = 'Exchange Rates'


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('from_currency', 'to_currency', 'rate', 'date', 'rate_display')
    list_filter = ('from_currency', 'to_currency', 'date', CurrencyExchangeFilter)
    search_fields = ('from_currency__code', 'to_currency__code')
    date_hierarchy = 'date'
    actions = ['export_as_csv']

    def rate_display(self, obj):
        return f"1 {obj.from_currency.code} = {obj.rate} {obj.to_currency.code}"

    rate_display.short_description = 'Exchange Rate'


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('name', 'amount_display', 'start_date', 'end_date',
                    'balance_display', 'expense_count', 'status_display')
    list_filter = ('currency', ('start_date', admin.DateFieldListFilter))
    search_fields = ('name',)
    date_hierarchy = 'start_date'
    actions = ['export_as_csv']
    inlines = [PosAllocationInline, GrantExpenseInline, DocumentProofInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', ('amount', 'currency'))
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
    )

    def get_currency_symbol(self, obj):
        """Helper method to safely get currency symbol"""
        try:
            if obj and obj.currency:
                return getattr(obj.currency, 'symbol', 'Rp')
        except AttributeError:
            pass
        return 'Rp'

    def amount_display(self, obj):
        if not obj:
            return '-'
        try:
            symbol = self.get_currency_symbol(obj)
            amount = f"{symbol}{obj.amount:,.2f}"
            return amount
        except (AttributeError, TypeError):
            return 'Rp0.00'

    amount_display.short_description = 'Amount'

    def balance_display(self, obj):
        if not obj:
            return '-'
        try:
            symbol = self.get_currency_symbol(obj)
            balance = obj.get_balance() if hasattr(obj, 'get_balance') else obj.amount
            color = 'green'
            if balance < 0:
                color = 'red'
            elif balance < obj.amount * 0.2:  # Less than 20% remaining
                color = 'orange'

            formatted_balance = f"{symbol}{balance:,.2f}"
            html = '<span style="color: {color}">{amount}</span>'.format(
                color=color,
                amount=formatted_balance
            )
            return format_html(html)
        except (AttributeError, TypeError):
            return format_html('<span style="color: gray">Rp0.00</span>')

    balance_display.short_description = 'Balance'

    def expense_count(self, obj):
        if not obj:
            return 0
        try:
            return obj.expenses.count()
        except AttributeError:
            return 0

    expense_count.short_description = 'Expenses'

    def status_display(self, obj):
        if not obj:
            return '-'
        try:
            if not hasattr(obj, 'get_balance'):
                return format_html('<span style="color: gray">Unknown</span>')

            balance = obj.get_balance()
            total = obj.amount or 0

            if total == 0:
                return format_html('<span style="color: gray">No Amount</span>')

            usage_percent = ((total - balance) / total) * 100

            if balance < 0:
                html = '<span style="color: red">Over Budget</span>'
            elif usage_percent >= 80:
                html = '<span style="color: orange">Warning</span>'
            else:
                html = '<span style="color: green">OK</span>'

            return format_html(html)

        except (AttributeError, TypeError, ZeroDivisionError):
            return format_html('<span style="color: gray">Error</span>')

    status_display.short_description = 'Status'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('fiscal_year', 'total_amount_display', 'allocated_amount_display',
                    'balance_display', 'usage_percentage', 'status_display')
    list_filter = ('currency', 'fiscal_year', BudgetStatusFilter)
    search_fields = ('fiscal_year',)
    actions = ['export_as_csv']
    inlines = [BudgetAllocationInline, PosAllocationInline, DocumentProofInline]

    fieldsets = (
        ('Budget Information', {
            'fields': (('fiscal_year', 'currency'),)
        }),
        ('Amounts', {
            'fields': ('initial_amount', 'additional_amount')
        }),
    )

    def get_currency_symbol(self, obj):
        """Helper method to safely get currency symbol with fallback"""
        if obj and obj.currency:
            return getattr(obj.currency, 'symbol', 'Rp')
        return 'Rp'  # Default fallback symbol

    def total_amount_display(self, obj):
        if not obj:
            return '-'
        symbol = self.get_currency_symbol(obj)
        try:
            return f"{symbol}{obj.get_total_amount():,.2f}"
        except (AttributeError, TypeError):
            return f"{symbol}0.00"

    total_amount_display.short_description = 'Total Amount'

    def allocated_amount_display(self, obj):
        if not obj:
            return '-'
        symbol = self.get_currency_symbol(obj)
        try:
            return f"{symbol}{obj.get_allocated_amount():,.2f}"
        except (AttributeError, TypeError):
            return f"{symbol}0.00"

    allocated_amount_display.short_description = 'Allocated'

    def balance_display(self, obj):
        if not obj:
            return '-'
        symbol = self.get_currency_symbol(obj)
        try:
            balance = obj.get_balance()
            color = 'green'
            if balance < 0:
                color = 'red'
            elif balance < obj.get_total_amount() * 0.2:
                color = 'orange'
            return format_html(
                '<span style="color: {}">{}{:,.2f}</span>',
                color, symbol, balance
            )
        except (AttributeError, TypeError, ZeroDivisionError):
            return format_html(
                '<span style="color: gray">{}{}</span>',
                symbol, '0.00'
            )

    balance_display.short_description = 'Balance'

    def usage_percentage(self, obj):
        if not obj:
            return '-'
        try:
            total_amount = obj.get_total_amount()
            if not total_amount:
                return '0%'
            allocated_amount = obj.get_allocated_amount()
            usage = (allocated_amount / total_amount) * 100
            color = 'green'
            if usage >= 100:
                color = 'red'
            elif usage >= 80:
                color = 'orange'

            # Format the percentage separately
            percentage_text = f'{usage:.1f}%'
            width_px = str(min(usage, 100))

            return format_html(
                '<div style="width:100px; background:#f8f9fa; border:1px solid #dee2e6;">'
                '<div style="width:{}px; height:20px; background:{}"></div>'
                '</div> {}',
                width_px, color, percentage_text
            )
        except (AttributeError, TypeError, ZeroDivisionError):
            return '0%'

    usage_percentage.short_description = 'Usage'

    def status_display(self, obj):
        if not obj:
            return '-'
        try:
            total_amount = obj.get_total_amount()
            if not total_amount:
                return format_html('<span style="color: gray">No Budget</span>')
            usage = (obj.get_allocated_amount() / total_amount) * 100
            if usage >= 100:
                return format_html('<span style="color: red">Over Budget</span>')
            elif usage >= 80:
                return format_html('<span style="color: orange">Warning</span>')
            return format_html('<span style="color: green">OK</span>')
        except (AttributeError, TypeError, ZeroDivisionError):
            return format_html('<span style="color: gray">Error</span>')

    status_display.short_description = 'Status'



@admin.register(PosAllocation)
class PosAllocationAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('name', 'amount_display', 'source_display',
                    'balance_display', 'expense_count', 'related_object_display')
    list_filter = ('currency', ('budget', admin.RelatedOnlyFieldListFilter),
                   ('grant', admin.RelatedOnlyFieldListFilter))
    search_fields = ('name', 'budget__fiscal_year', 'grant__name')
    actions = ['export_as_csv']
    inlines = [PosExpenseInline, DocumentProofInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            expense_count=Count('expenses'),
            expenses_sum=Sum('expenses__amount')
        ).select_related(
            'currency', 'budget', 'grant', 'content_type'
        )

    def amount_display(self, obj):
        if not obj:
            return '-'
        try:
            return str(obj.amount)  # MoneyField has its own string representation
        except (AttributeError, TypeError, ValueError):
            return 'Rp0.00'

    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

    def source_display(self, obj):
        if not obj:
            return '-'
        try:
            if obj.budget:
                return f"Budget: {obj.budget.fiscal_year}"
            if obj.grant:
                return f"Grant: {obj.grant.name}"
        except AttributeError:
            pass
        return "-"

    source_display.short_description = 'Source'

    def balance_display(self, obj):
        if not obj:
            return '-'
        try:
            # Get expenses sum from annotation
            expenses_sum = obj.expenses_sum or 0
            balance = float(obj.amount.amount) - float(expenses_sum)

            color = 'green'
            if balance < 0:
                color = 'red'
            elif balance < float(obj.amount.amount) * 0.2:
                color = 'orange'

            html = '<span style="color: {color}">{amount}</span>'.format(
                color=color,
                amount=obj.amount.__class__(balance, obj.amount.currency)
            )
            return format_html(html)
        except (AttributeError, TypeError, ValueError):
            return format_html('<span style="color: gray">Rp0.00</span>')

    balance_display.short_description = 'Balance'

    def expense_count(self, obj):
        try:
            return obj.expense_count
        except AttributeError:
            return 0

    expense_count.short_description = 'Expenses'
    expense_count.admin_order_field = 'expense_count'

    def related_object_display(self, obj):
        if not obj:
            return '-'
        try:
            if obj.content_type and obj.object_id and obj.content_object:
                return str(obj.content_object)
        except (AttributeError, ContentType.DoesNotExist):
            pass
        return '-'

    related_object_display.short_description = 'Related To'

    def clean_form(self, form):
        """Validates that allocation can't be associated with both budget and grant"""
        cleaned_data = form.cleaned_data
        if cleaned_data.get('budget') and cleaned_data.get('grant'):
            raise ValidationError(
                "A POS allocation must be associated with either a budget or a grant, not both."
            )
        if not cleaned_data.get('budget') and not cleaned_data.get('grant'):
            raise ValidationError(
                "A POS allocation must be associated with either a budget or a grant."
            )
        return cleaned_data

    def save_model(self, request, obj, form, change):
        """Handle currency and validation before saving"""
        try:
            # Set currency from MoneyField if not explicitly set
            if not obj.currency and obj.amount:
                obj.currency = obj.amount.currency

            # Set currency from budget/grant if available
            if not obj.currency:
                if obj.budget and obj.budget.currency:
                    obj.currency = obj.budget.currency
                elif obj.grant and obj.grant.currency:
                    obj.currency = obj.grant.currency

            obj.full_clean()  # Run model validation
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Validation error: {str(e)}", level='ERROR')
            raise  # Re-raise to prevent saving
        except Exception as e:
            self.message_user(request, f"Error saving allocation: {str(e)}", level='ERROR')
            raise

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Optimize foreign key choices"""
        if db_field.name == "budget":
            kwargs["queryset"] = db_field.related_model.objects.select_related('currency')
        elif db_field.name == "grant":
            kwargs["queryset"] = db_field.related_model.objects.select_related('currency')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('date', 'description', 'amount_display',
                    'debit_account', 'credit_account', 'related_object_display')
    list_filter = ('date', 'currency', 'debit_account', 'credit_account')
    search_fields = ('description', 'debit_account', 'credit_account')
    date_hierarchy = 'date'
    actions = ['export_as_csv']

    readonly_fields = ('related_object_display',)

    def get_currency_symbol(self, obj):
        """Helper method to safely get currency symbol"""
        try:
            if obj and obj.currency:
                return getattr(obj.currency, 'symbol', 'Rp')
            if obj and obj.amount and obj.amount.currency:
                return obj.amount.currency.symbol
        except AttributeError:
            pass
        return 'Rp'

    def amount_display(self, obj):
        if not obj:
            return '-'
        try:
            # Handle MoneyField which already includes currency information
            if hasattr(obj.amount, 'currency') and hasattr(obj.amount, 'amount'):
                return str(obj.amount)

            # Fallback to manual formatting if needed
            symbol = self.get_currency_symbol(obj)
            amount = float(obj.amount.amount if hasattr(obj.amount, 'amount') else obj.amount)
            return f"{symbol}{amount:,.2f}"
        except (AttributeError, TypeError, ValueError):
            return 'Rp0.00'

    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

    def related_object_display(self, obj):
        if not obj:
            return '-'
        try:
            if obj.content_type and obj.object_id and obj.related_object:
                return str(obj.related_object)
        except (AttributeError, ContentType.DoesNotExist):
            pass
        return '-'

    related_object_display.short_description = 'Related To'

    def get_queryset(self, request):
        """Optimize queryset by selecting related fields"""
        queryset = super().get_queryset(request)
        return queryset.select_related('currency', 'content_type')

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly based on permissions"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # Editing existing object
            if not request.user.is_superuser:
                readonly_fields.extend(['amount', 'currency', 'date'])
        return readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            if not obj.currency and obj.amount and hasattr(obj.amount, 'currency'):
                obj.currency = obj.amount.currency
            super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, f"Error saving entry: {str(e)}", level='ERROR')


@admin.register(DocumentProof)
class DocumentProofAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('description', 'upload_date', 'file_link', 'related_object_display')
    list_filter = ('upload_date', 'content_type')
    search_fields = ('description',)
    date_hierarchy = 'upload_date'
    actions = ['export_as_csv']

    def file_link(self, obj):
        return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)

    file_link.short_description = 'File'

    def related_object_display(self, obj):
        return str(obj.content_object)

    related_object_display.short_description = 'Related To'


@admin.register(GrantExpense)
class GrantExpenseAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('date', 'description', 'amount_display', 'grant_display',
                    'document_count')
    list_filter = (
        'date',
        'currency',
        ('grant', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = ('description', 'grant__name')
    date_hierarchy = 'date'
    readonly_fields = ('document_count',)
    actions = ['export_as_csv']

    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'description')
        }),
        ('Financial Details', {
            'fields': (('amount', 'currency'), 'grant')
        }),
        ('Documentation', {
            'fields': ('document_count',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'grant', 'currency'
        ).prefetch_related(
            'document_proof'
        ).annotate(
            doc_count=Count('document_proof')
        )

    def amount_display(self, obj):
        if not obj:
            return '-'
        try:
            return str(obj.amount)  # Use MoneyField's string representation
        except (AttributeError, TypeError):
            return '$0.00'

    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

    def grant_display(self, obj):
        if not obj or not obj.grant:
            return '-'
        try:
            return format_html(
                '<span title="Balance: {}">{}</span>',
                obj.grant.get_balance(),
                obj.grant.name
            )
        except (AttributeError, TypeError):
            return obj.grant.name

    grant_display.short_description = 'Grant'
    grant_display.admin_order_field = 'grant__name'

    def document_count(self, obj):
        if not obj:
            return 0
        try:
            return obj.doc_count
        except AttributeError:
            return obj.document_proof.count()

    document_count.short_description = 'Documents'
    document_count.admin_order_field = 'doc_count'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "grant":
            kwargs["queryset"] = db_field.related_model.objects.select_related(
                'currency'
            ).annotate(
                balance=ExpressionWrapper(
                    F('amount') - Subquery(
                        GrantExpense.objects.filter(
                            grant=OuterRef('pk')
                        ).values('grant').annotate(
                            total=Sum('amount')
                        ).values('total')[:1]
                    ),
                    output_field=DecimalField()
                )
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def clean_form(self, form):
        """Validate currency matches and grant has sufficient balance"""
        cleaned_data = form.cleaned_data
        if not cleaned_data:
            return cleaned_data

        grant = cleaned_data.get('grant')
        currency = cleaned_data.get('currency')
        amount = cleaned_data.get('amount')

        if grant and currency and grant.currency != currency:
            raise ValidationError({
                'currency': 'Expense currency must match grant currency'
            })

        if grant and amount:
            # Check if this would exceed grant balance
            current_expense = self.instance
            additional_amount = amount
            if current_expense and current_expense.pk:
                additional_amount -= current_expense.amount

            if additional_amount > grant.get_balance():
                raise ValidationError({
                    'amount': 'This expense would exceed the grant balance'
                })

        return cleaned_data

    def save_model(self, request, obj, form, change):
        try:
            # Ensure currency matches grant's currency
            if obj.grant and not obj.currency:
                obj.currency = obj.grant.currency

            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, str(e), level='ERROR')
            raise
        except Exception as e:
            self.message_user(
                request,
                f"Error saving expense: {str(e)}",
                level='ERROR'
            )
            raise

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }

# Admin Site Configuration
admin.site.site_header = 'Financial Management System'
admin.site.site_title = 'Financial Management'
admin.site.index_title = 'Financial Administration'