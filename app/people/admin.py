from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.html import format_html
from .models import *
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.admin.models import LogEntry

#LogEntry.objects.all().delete()

class RelationshipInline(admin.TabularInline):
    model = Relationship
    fk_name = 'person'
    extra = 1
    fields = ('related_person', 'relationship_type', 'kontak_darurat')

class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False




class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'is_active', 'is_staff')
    list_filter = ('email', 'user_type',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'user_type')}),
        ('OAuth info', {'fields': ('oauth_provider', 'oauth_token', 'oauth_refresh_token', 'oauth_token_expiry')}),
        ('Permissions', {'fields': ('is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_type', 'password1', 'password2')}
         ),
    )

    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'user_type', 'display_image', 'extension')
    list_filter = ('user__user_type',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    inlines = [RelationshipInline, StaffInline]

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'

    def user_type(self, obj):
        return obj.user.user_type if obj.user else 'N/A'
    user_type.short_description = 'User Type'

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Profile Picture'

@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('person', 'related_person', 'relationship_type', 'kontak_darurat')
    list_filter = ('relationship_type', 'kontak_darurat')
    search_fields = ('person__first_name', 'person__last_name', 'related_person__first_name', 'related_person__last_name')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('person', 'employee_id', 'department', 'position', 'hire_date')
    list_filter = ('department', 'hire_date')
    search_fields = ('person__first_name', 'person__last_name', 'employee_id', 'position')

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name','phone','address')
    list_filter = ('name',)
    search_fields = ('name',)
# Unregister the Group model from admin.
# If you want to use it, you'll need to define a custom GroupAdmin
from django.contrib.auth.models import Group
admin.site.unregister(Group)


class PhotoInline(admin.TabularInline):
    model = Photo
    readonly_fields = ('google_photo_id', 'filename', 'mime_type', 'downloaded_at', 'photo_file')
    extra = 0
    can_delete = False
    max_num = 0

@admin.register(PhotoBackup)
class PhotoBackupAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_photos', 'created_at', 'photos_limit')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('status', 'total_photos', 'error_message', 'created_at', 'updated_at')
    inlines = [PhotoInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'pending':  # If backup has started, make photos_limit readonly
            return self.readonly_fields + ('photos_limit',)
        return self.readonly_fields