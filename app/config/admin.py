from django.contrib import admin
from .models import Category, Option

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','id', 'description', 'is_active', 'created_by', 'created_at', 'updated_by', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ( 'name','id','category', 'value', 'is_active', 'order', 'created_by', 'created_at', 'updated_by', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'value', 'description')
    ordering = ('category', 'order', 'name')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)