from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import *


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            FiscalYear.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = (
    'reference_number', 'donor', 'amount', 'currency', 'start_date', 'end_date', 'grant_type', 'get_balance')
    list_filter = ('grant_type', 'donor', 'currency')
    search_fields = ('reference_number', 'donor__name', 'description')
    readonly_fields = ('get_balance',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'grant_type', 'donor', 'reference_number')
        }),
        ('Financial Details', {
            'fields': ('amount', 'currency', 'start_date', 'end_date', 'reporting_frequency')
        }),
        ('Status', {
            'fields': ('get_balance',)
        })
    )

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'currency', 'expense_type', 'status', 'get_funding_source')
    list_filter = ('status', 'expense_type', 'currency', 'cost_center')
    search_fields = ('description', 'notes')
    readonly_fields = ('submitted_date', 'approved_date')

    def get_funding_source(self, obj):
        return str(obj.funding_source)
    get_funding_source.short_description = 'Funding Source'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'currency', 'cost_center', 'content_type',
            'submitted_by', 'approved_by'
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(
                model__in=['grant', 'budget']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'fiscal_year', 'budget_type', 'get_total_budget', 'currency', 'get_balance')
    list_filter = ('budget_type', 'fiscal_year', 'currency')
    search_fields = ('name', 'description')

    def get_total_budget(self, obj):
        return format_html(
            '{} {}<br><small class="text-muted">Initial: {} | Revised: {}</small>',
            obj.get_total_budget(),
            obj.currency.symbol,
            obj.initial_amount,
            obj.revised_amount
        )

    get_total_budget.short_description = 'Total Budget'


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent')
    search_fields = ('code', 'name')
    list_filter = ('parent',)




@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_person', 'email')


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('date', 'from_currency', 'to_currency', 'rate')
    list_filter = ('from_currency', 'to_currency', 'date')
    date_hierarchy = 'date'


@admin.register(SupportingDocument)
class SupportingDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'document_number', 'document_date', 'verified_by')
    list_filter = ('document_type', 'verified_by')
    search_fields = ('document_number', 'description')
    readonly_fields = ('verification_date',)

    def save_model(self, request, obj, form, change):
        if not change:  # New document
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)