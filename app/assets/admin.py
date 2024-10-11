from django.contrib import admin
from django.utils.html import format_html
from .models import Asset, Maintenance, Depreciation, Inventory, AssetLifecycle, Compliance, Supplier, Procurement, AssetAssignment

class MaintenanceInline(admin.TabularInline):
    model = Maintenance
    extra = 1

class DepreciationInline(admin.TabularInline):
    model = Depreciation
    extra = 1

class AssetLifecycleInline(admin.TabularInline):
    model = AssetLifecycle
    extra = 1

class ComplianceInline(admin.TabularInline):
    model = Compliance
    extra = 1

class ProcurementInline(admin.TabularInline):
    model = Procurement
    extra = 1

class AssetAssignmentInline(admin.TabularInline):
    model = AssetAssignment
    extra = 1

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_id', 'category', 'status', 'purchase_date', 'current_value', 'location', 'image_preview')
    list_filter = ('category', 'status', 'purchase_date')
    search_fields = ('name', 'asset_id', 'location')
    date_hierarchy = 'purchase_date'
    readonly_fields = ('image_preview',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'asset_id', 'category', 'status', 'image', 'image_preview')
        }),
        ('Financial Details', {
            'fields': ('purchase_date', 'purchase_price', 'current_value')
        }),
        ('Additional Information', {
            'fields': ('warranty_expiration', 'location')
        }),
    )
    inlines = [MaintenanceInline, DepreciationInline, AssetLifecycleInline, ComplianceInline, ProcurementInline, AssetAssignmentInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('asset', 'maintenance_type', 'maintenance_date', 'next_maintenance_date', 'cost', 'performed_by')
    list_filter = ('maintenance_type', 'maintenance_date')
    search_fields = ('asset__name', 'asset__asset_id', 'performed_by')
    date_hierarchy = 'maintenance_date'

@admin.register(Depreciation)
class DepreciationAdmin(admin.ModelAdmin):
    list_display = ('asset', 'depreciation_date', 'depreciation_amount', 'remaining_value')
    list_filter = ('depreciation_date',)
    search_fields = ('asset__name', 'asset__asset_id')
    date_hierarchy = 'depreciation_date'

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('asset', 'stock_quantity', 'reorder_threshold')
    list_filter = ('stock_quantity', 'reorder_threshold')
    search_fields = ('asset__name', 'asset__asset_id')

@admin.register(AssetLifecycle)
class AssetLifecycleAdmin(admin.ModelAdmin):
    list_display = ('asset', 'stage', 'image', 'date')
    list_filter = ('stage', 'date')
    search_fields = ('asset__name', 'asset__asset_id')
    date_hierarchy = 'date'

@admin.register(Compliance)
class ComplianceAdmin(admin.ModelAdmin):
    list_display = ('asset', 'compliance_type', 'status', 'last_checked', 'next_check_due')
    list_filter = ('compliance_type', 'status', 'last_checked')
    search_fields = ('asset__name', 'asset__asset_id')
    date_hierarchy = 'last_checked'

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'email')
    search_fields = ('name', 'contact_person', 'email')

@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    list_display = ('asset', 'supplier', 'procurement_date', 'cost', 'payment_status')
    list_filter = ('procurement_date', 'payment_status')
    search_fields = ('asset__name', 'asset__asset_id', 'supplier__name')
    date_hierarchy = 'procurement_date'

@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ('asset', 'user', 'assigned_date', 'return_date')
    list_filter = ('assigned_date', 'return_date')
    search_fields = ('asset__name', 'asset__asset_id', 'user__username')
    date_hierarchy = 'assigned_date'