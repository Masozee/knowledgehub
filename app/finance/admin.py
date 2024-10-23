from django.contrib import admin
from django.db.models import Sum, F
from django.utils.html import format_html
from .models import Currency, ExchangeRate, JournalEntry, Grant, Budget, BudgetAllocation, PosAllocation, DocumentProof, \
    GrantExpense, PosExpense


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')


class ExchangeRateInline(admin.TabularInline):
    model = ExchangeRate
    fk_name = 'from_currency'
    extra = 1


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('from_currency', 'to_currency', 'rate', 'date')
    list_filter = ('from_currency', 'to_currency', 'date')
    date_hierarchy = 'date'
    search_fields = ('from_currency__code', 'to_currency__code')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'debit_account', 'credit_account', 'formatted_amount', 'related_object_link')
    list_filter = ('date', 'debit_account', 'credit_account')
    search_fields = ('description', 'debit_account', 'credit_account')
    date_hierarchy = 'date'

    def formatted_amount(self, obj):
        return f"{obj.amount.currency.symbol}{obj.amount.amount}"

    formatted_amount.short_description = 'Amount'

    def related_object_link(self, obj):
        if obj.related_object:
            return format_html('<a href="{}">{}</a>',
                               admin.site.reverse(
                                   f'admin:{obj.related_object._meta.app_label}_{obj.related_object._meta.model_name}_change',
                                   args=[obj.object_id]),
                               str(obj.related_object)
                               )
        return '-'

    related_object_link.short_description = 'Related Object'


class GrantExpenseInline(admin.TabularInline):
    model = GrantExpense
    extra = 1


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_amount', 'start_date', 'end_date', 'balance', 'pos_balance')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)
    inlines = [GrantExpenseInline]

    def formatted_amount(self, obj):
        return f"{obj.amount.currency.symbol}{obj.amount.amount}"

    formatted_amount.short_description = 'Amount'

    def balance(self, obj):
        return f"IDR {obj.get_balance():.2f}"

    def pos_balance(self, obj):
        return f"IDR {obj.get_pos_balance():.2f}"


class BudgetAllocationInline(admin.TabularInline):
    model = BudgetAllocation
    extra = 1


class PosAllocationInline(admin.TabularInline):
    model = PosAllocation
    extra = 1
    fk_name = 'budget'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
    'fiscal_year', 'formatted_initial_amount', 'formatted_additional_amount', 'total_amount', 'allocated_amount',
    'balance', 'pos_balance')
    list_filter = ('fiscal_year',)
    search_fields = ('fiscal_year',)
    inlines = [BudgetAllocationInline, PosAllocationInline]

    def formatted_initial_amount(self, obj):
        return f"{obj.initial_amount.currency.symbol}{obj.initial_amount.amount}"

    formatted_initial_amount.short_description = 'Initial Amount'

    def formatted_additional_amount(self, obj):
        return f"{obj.additional_amount.currency.symbol}{obj.additional_amount.amount}"

    formatted_additional_amount.short_description = 'Additional Amount'

    def total_amount(self, obj):
        return f"IDR {obj.get_total_amount():.2f}"

    def allocated_amount(self, obj):
        return f"IDR {obj.get_allocated_amount():.2f}"

    def balance(self, obj):
        return f"IDR {obj.get_balance():.2f}"

    def pos_balance(self, obj):
        return f"IDR {obj.get_pos_balance():.2f}"


@admin.register(BudgetAllocation)
class BudgetAllocationAdmin(admin.ModelAdmin):
    list_display = ('budget', 'category', 'formatted_amount')
    list_filter = ('budget', 'category')
    search_fields = ('category',)

    def formatted_amount(self, obj):
        return f"{obj.amount.currency.symbol}{obj.amount.amount}"

    formatted_amount.short_description = 'Amount'


class PosExpenseInline(admin.TabularInline):
    model = PosExpense
    extra = 1


@admin.register(PosAllocation)
class PosAllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_amount', 'budget', 'grant', 'balance')
    list_filter = ('budget', 'grant')
    search_fields = ('name',)
    inlines = [PosExpenseInline]

    def formatted_amount(self, obj):
        return f"{obj.amount.currency.symbol}{obj.amount.amount}"

    formatted_amount.short_description = 'Amount'

    def balance(self, obj):
        return f"IDR {obj.get_balance():.2f}"


@admin.register(DocumentProof)
class DocumentProofAdmin(admin.ModelAdmin):
    list_display = ('file', 'upload_date', 'description', 'content_type', 'get_related_object_str')
    list_filter = ('upload_date', 'content_type')
    search_fields = ('description',)
    date_hierarchy = 'upload_date'


@admin.register(GrantExpense)
class GrantExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'grant', 'description', 'formatted_amount', 'document_proof')
    list_filter = ('date', 'grant')
    search_fields = ('description',)
    date_hierarchy = 'date'

    def formatted_amount(self, obj):
        return f"{obj.amount.currency.symbol}{obj.amount.amount}"

    formatted_amount.short_description = 'Amount'


@admin.register(PosExpense)
class PosExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'pos_allocation', 'description', 'formatted_amount', 'document_proof')
    list_filter = ('date', 'pos_allocation')
    search_fields = ('description',)
    date_hierarchy = 'date'

    def formatted_amount(self, obj):
        return f"{obj.amount.currency.symbol}{obj.amount.amount}"

    formatted_amount.short_description = 'Amount'