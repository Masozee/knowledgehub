from django.contrib import admin
from django.contrib import messages
from .models import DatabaseBackup

@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'timestamp', 'file_size', 'formatted_file_size')
    list_filter = ('timestamp',)
    search_fields = ('file_name',)
    readonly_fields = ('timestamp', 'file_name', 'file_size', 'formatted_file_size')
    ordering = ('-timestamp',)
    actions = ['restore_backup']

    def formatted_file_size(self, obj):
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    formatted_file_size.short_description = 'File Size'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def restore_backup(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one backup to restore.", level=messages.WARNING)
            return

        backup = queryset.first()
        try:
            backup.restore()
            self.message_user(request, f"Successfully restored database from backup: {backup.file_name}", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error restoring database: {str(e)}", level=messages.ERROR)

    restore_backup.short_description = "Restore selected backup"