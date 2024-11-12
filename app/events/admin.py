from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import (
    EventCategory, Event, Speaker, SpeakerAttachment,
    TicketType, Ticket, EventReview
)
from app.people.models import CustomUser


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_events_count')
    search_fields = ('name',)

    def get_events_count(self, obj):
        return obj.event_set.count()

    get_events_count.short_description = 'Events Count'


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1
    fields = ('name', 'price', 'quantity', 'remaining', 'sale_start_date', 'sale_end_date', 'is_active')


class SpeakerInline(admin.TabularInline):
    model = Speaker
    extra = 1
    fields = ('person', 'speaker_type', 'presentation_title', 'speaking_slot_start', 'speaking_slot_end', 'order')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'status',
                    'current_capacity', 'max_capacity', 'get_tickets_sold')
    list_filter = ('status', 'category', 'start_date')
    search_fields = ('title', 'description', 'venue_name',
                     'organizer__email', 'organizer__first_name', 'organizer__last_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    raw_id_fields = ('organizer',)  # Added for better CustomUser selection

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category', 'organizer', 'status')
        }),
        ('Timing & Location', {
            'fields': ('start_date', 'end_date', 'location', 'venue_name', 'address')
        }),
        ('Capacity', {
            'fields': ('max_capacity', 'current_capacity')
        }),
        ('Media', {
            'fields': ('featured_image',),
            'classes': ('collapse',)
        })
    )

    inlines = [TicketTypeInline, SpeakerInline]

    def get_tickets_sold(self, obj):
        return Ticket.objects.filter(ticket_type__event=obj).count()

    get_tickets_sold.short_description = 'Tickets Sold'


# ... [Previous SpeakerAdmin and SpeakerAttachmentAdmin remain the same] ...

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'ticket_type', 'attendee_name', 'status',
                    'is_checked_in', 'purchase_date', 'get_user_email')
    list_filter = ('status', 'is_checked_in', 'purchase_date', 'ticket_type__event')
    search_fields = ('ticket_number', 'attendee_name', 'attendee_email',
                     'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('ticket_number', 'purchase_date')
    raw_id_fields = ('user',)  # Added for better CustomUser selection

    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'ticket_type', 'status')
        }),
        ('Attendee Information', {
            'fields': ('user', 'attendee_name', 'attendee_email')
        }),
        ('Check-in Status', {
            'fields': ('is_checked_in', 'checked_in_at')
        })
    )

    def get_user_email(self, obj):
        return obj.user.email

    get_user_email.short_description = 'User Email'

    actions = ['mark_as_checked_in', 'mark_as_cancelled']

    def mark_as_checked_in(self, request, queryset):
        queryset.update(is_checked_in=True, checked_in_at=timezone.now())

    mark_as_checked_in.short_description = "Mark selected tickets as checked in"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')

    mark_as_cancelled.short_description = "Mark selected tickets as cancelled"


@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'get_user_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'event')
    search_fields = ('event__title', 'user__email', 'user__first_name',
                     'user__last_name', 'comment')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)  # Added for better CustomUser selection

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    get_user_name.short_description = 'User'


# Customize admin site header and title
admin.site.site_header = 'Event Management Administration'
admin.site.site_title = 'Event Management Admin Portal'
admin.site.index_title = 'Welcome to Event Management Portal'