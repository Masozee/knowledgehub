from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.html import format_html
from .models import *

class RelationshipInline(admin.TabularInline):
    model = Relationship
    fk_name = 'person'
    extra = 1
    fields = ('related_person', 'relationship_type', 'kontak_darurat')

class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False

class SpeakerInline(admin.StackedInline):
    model = Speaker
    can_delete = False

class WriterInline(admin.StackedInline):
    model = Writer
    can_delete = False

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('user_type',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('user_type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('username', 'email', 'user_type')

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'user_type', 'display_image')
    list_filter = ('user__user_type',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    inlines = [RelationshipInline, StaffInline, SpeakerInline, WriterInline]

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

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('person', 'areas_of_expertise', 'speaking_fee')
    search_fields = ('person__first_name', 'person__last_name', 'areas_of_expertise')

@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ('person', 'genre')
    list_filter = ('genre',)
    search_fields = ('person__first_name', 'person__last_name', 'genre', 'publications')

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