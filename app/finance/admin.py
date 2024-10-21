# In finance/admin.py

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.db.models import Sum
from .models import *


class JournalEntryInline(GenericTabularInline):
    model = JournalEntry
    extra = 0
    fields = ('date', 'description', 'debit_account', 'credit_account', 'amount')
    readonly_fields = ('date', 'description', 'debit_account', 'credit_account', 'amount')


class DocumentProofInline(GenericTabularInline):
    model = DocumentProof
    extra = 1
    fields = ('file', 'description')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'debit_account', 'credit_account', 'amount', 'get_related_object')
    list_filter = ('date', 'debit_account', 'credit_account')
    search_fields = ('description', 'debit_account', 'credit_account')
    date_hierarchy = 'date'

    def get_related_object(self, obj):
        if obj.related_object:
            return f"{obj.related_object._meta.model_name}: {obj.related_object}"
        return "None"

    get_related_object.short_description = 'Related Object'


class GrantExpenseInline(admin.TabularInline):
    model = GrantExpense
    extra = 1
    show_change_link = True


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'amount', 'start_date', 'end_date', 'get_balance', 'get_pos_allocated_amount', 'get_pos_remaining_amount',
    'progress_bar')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)
    inlines = [GrantExpenseInline, JournalEntryInline]

    def get_balance(self, obj):
        return obj.get_balance()

    get_balance.short_description = 'Remaining Balance'

    def get_pos_allocated_amount(self, obj):
        return sum(allocation.amount for allocation in obj.pos_allocations.all())

    get_pos_allocated_amount.short_description = 'POS Allocated Amount'

    def get_pos_remaining_amount(self, obj):
        return obj.get_pos_balance()

    get_pos_remaining_amount.short_description = 'POS Remaining Amount'

    def progress_bar(self, obj):
        total = obj.amount
        spent = total - obj.get_balance()
        percentage = int((spent / total) * 100)
        return format_html(
            '<div style="width:100px;background-color:#ddd;">'
            '<div style="width:{}px;height:20px;background-color:{};">&nbsp;</div>'
            '</div> {}%',
            percentage, '#0F0' if percentage < 80 else '#F00', percentage
        )

    progress_bar.short_description = 'Spend Progress'


@admin.register(GrantExpense)
class GrantExpenseAdmin(admin.ModelAdmin):
    list_display = ('grant', 'description', 'amount', 'date')
    list_filter = ('grant', 'date')
    search_fields = ('description', 'grant__name')
    date_hierarchy = 'date'
    inlines = [DocumentProofInline, JournalEntryInline]


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
    'fiscal_year', 'total_amount', 'get_allocated_amount', 'get_remaining_amount', 'get_pos_allocated_amount',
    'get_pos_remaining_amount')
    inlines = [BudgetAllocationInline, PosAllocationInline, JournalEntryInline]

    def get_allocated_amount(self, obj):
        return sum(allocation.amount for allocation in obj.allocations.all())

    get_allocated_amount.short_description = 'Allocated Amount'

    def get_remaining_amount(self, obj):
        return obj.get_balance()

    get_remaining_amount.short_description = 'Remaining Amount'

    def get_pos_allocated_amount(self, obj):
        return sum(allocation.amount for allocation in obj.pos_allocations.all())

    get_pos_allocated_amount.short_description = 'POS Allocated Amount'

    def get_pos_remaining_amount(self, obj):
        return obj.get_pos_balance()

    get_pos_remaining_amount.short_description = 'POS Remaining Amount'


@admin.register(BudgetAllocation)
class BudgetAllocationAdmin(admin.ModelAdmin):
    list_display = ('budget', 'category', 'amount')
    list_filter = ('budget', 'category')
    search_fields = ('category',)
    inlines = [JournalEntryInline]


@admin.register(PosAllocation)
class PosAllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'get_source', 'get_balance')
    list_filter = ('budget', 'grant')
    search_fields = ('name',)
    inlines = [JournalEntryInline]

    def get_source(self, obj):
        return obj.budget or obj.grant

    get_source.short_description = 'Source'

    def get_balance(self, obj):
        return obj.get_balance()

    get_balance.short_description = 'Remaining Balance'


@admin.register(PosExpense)
class PosExpenseAdmin(admin.ModelAdmin):
    list_display = ('pos_allocation', 'description', 'amount', 'date')
    list_filter = ('pos_allocation', 'date')
    search_fields = ('description', 'pos_allocation__name')
    date_hierarchy = 'date'
    inlines = [DocumentProofInline, JournalEntryInline]


@admin.register(DocumentProof)
class DocumentProofAdmin(admin.ModelAdmin):
    list_display = ('description', 'file', 'upload_date', 'get_related_object')
    list_filter = ('upload_date',)
    search_fields = ('description',)
    date_hierarchy = 'upload_date'

    def get_related_object(self, obj):
        return obj.get_related_object_str()
    get_related_object.short_description = 'Related Object'