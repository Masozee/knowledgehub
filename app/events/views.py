# views.py
from django.views.generic import ListView, DetailView
from django.db.models import Prefetch
from .models import *


class index(ListView):
    model = Event
    template_name = 'dashboard/events/index.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        queryset = Event.objects.select_related(
            'category',
            'organizer'
        ).filter(
            status='published'
        )

        # Filter by category if provided
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Filter by date range
        start_date = self.request.GET.get('start_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)

        end_date = self.request.GET.get('end_date')
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = EventCategory.objects.all()
        return context


class detail(DetailView):
    model = Event
    template_name = 'dashboard/events/detail.html'
    context_object_name = 'event'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Event.objects.select_related(
            'category',
            'organizer'
        ).prefetch_related(
            Prefetch(
                'event_speakers',
                queryset=Speaker.objects.select_related('person').order_by('order'),
                to_attr='ordered_speakers'
            ),
            Prefetch(
                'event_speakers__speaker_attachments',
                queryset=SpeakerAttachment.objects.filter(is_public=True),
                to_attr='public_attachments'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_full'] = self.object.is_full()
        return context