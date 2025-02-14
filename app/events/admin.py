from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import (
    EventCategory, Event, Speaker, SpeakerAttachment,
)
from app.people.models import CustomUser


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_events_count')
    search_fields = ('name',)

    def get_events_count(self, obj):
        return obj.event_set.count()

    get_events_count.short_description = 'Events Count'



class SpeakerInline(admin.TabularInline):
    model = Speaker
    extra = 1
    fields = ('person', 'speaker_type', 'presentation_title', 'speaking_slot_start', 'speaking_slot_end', 'order')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'status',
                    'project', 'max_capacity')
    list_filter = ('status', 'category', 'start_date')
    search_fields = ('title', 'description', 'venue_name',
                     'organizer__email', 'organizer__first_name', 'organizer__last_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    raw_id_fields = ('organizer',)  # Added for better CustomUser selection

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category', 'organizer','project' ,'status')
        }),
        ('Timing & Location', {
            'fields': ('start_date', 'end_date', 'location', 'venue_name', 'address')
        }),
        ('Capacity', {
            'fields': ('max_capacity', 'current_capacity')
        }),
        ('Media', {
            'fields': ('featured_image', 'youtube', 'register'),
            'classes': ('collapse',)
        })
    )

    inlines = [SpeakerInline]



# Customize admin site header and title
admin.site.site_header = 'Knowledgehub Administration'
admin.site.site_title = 'Knowledgehub Admin Portal'
admin.site.index_title = 'Welcome to Knowledgehub Portal'