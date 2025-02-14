from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .models import *
from django.db.models import Count, Sum
from .forms import *

#from another models
from app.people.models import *

class index(ListView):
    model = Publication
    template_name = 'dashboard/publications/index.html'
    context_object_name = 'publications'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status', 'all')

        # Base queryset with necessary relations
        queryset = queryset.select_related('category').prefetch_related(
            'authors', 'publicationauthor_set'
        ).order_by('-date_publish')

        # Filter based on status
        if status_filter == 'published':
            queryset = queryset.filter(status='published', publish=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(status='draft')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', 'all')
        return context

def detail(request):
    return render(request, 'dashboard/publications/detail.html')

class PublicationDetailView(DetailView):
    model = Publication
    template_name = 'dashboard/publications/detail.html'
    context_object_name = 'publication'

    def get_queryset(self):
        # Optimize the queryset with related fields
        return Publication.objects.select_related(
            'category',
            'project',
            'stats'
        ).prefetch_related(
            'publicationauthor_set__author',
            'editor',
            'partners',
            'topic',
            'tags'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context
        publication = self.object
        context.update({
            'authors': publication.publicationauthor_set.select_related('author').order_by('order'),
            'corresponding_author': publication.publicationauthor_set.filter(
                is_corresponding=True
            ).select_related('author').first(),
            'related_publications': Publication.objects.filter(
                category=publication.category
            ).exclude(id=publication.id)[:3],
        })
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Record view if not ajax request
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object.record_view(
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
        return response

class PublicationDownloadView(LoginRequiredMixin, DetailView):
    model = Publication

    def get(self, request, *args, **kwargs):
        publication = self.get_object()
        if not publication.file:
            return HttpResponseRedirect(reverse('publication-detail', kwargs={'slug': publication.slug}))

        # Record download
        publication.record_download(
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )

        return HttpResponseRedirect(publication.file.url)

class PublicationListView(ListView):
    model = Publication
    template_name = 'dashboard/publications/list.html'
    context_object_name = 'publications'
    paginate_by = 9  # Show 9 publications per page (3x3 grid)

    def get_queryset(self):
        # Base queryset
        queryset = Publication.objects.filter(
            status='published',
            publish=True
        ).select_related(
            'category'
        ).prefetch_related(
            'publicationauthor_set__author'
        ).order_by('-date_publish')

        # Get search query
        form = PublicationSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            if q:
                # Updated search filter to correctly reference author fields
                queryset = queryset.filter(
                    Q(title__icontains=q) |
                    Q(authors__first_name__icontains=q) |
                    Q(authors__last_name__icontains=q)
                ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PublicationSearchForm(self.request.GET)
        return context


class AuthorListView(ListView):
    model = Person
    template_name = 'dashboard/publications/author_list.html'
    context_object_name = 'authors'

    def get_queryset(self):
        return Person.objects.annotate(
            publication_count=Count('authored_publications', distinct=True),
            total_visits=Sum('authored_publications__viewed'),
            total_downloads=Sum('authored_publications__download_count')
        ).order_by('-publication_count')


class PublicationTopicListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/publications/topics.html'
    context_object_name = 'topic_stats'
    paginate_by = 20

    def get_queryset(self):
        return Publication.get_topic_stats()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_section'] = 'topics'  # For navigation highlighting
        return context

class PublicationTagListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/publications/tags.html'
    context_object_name = 'tag_stats'
    paginate_by = 20

    def get_queryset(self):
        return Publication.get_tag_stats()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_section'] = 'tags'
        return context

class PublicationSubmissionListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/publications/submissions.html'
    context_object_name = 'submissions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Publication.objects.exclude(
            status='published'
        ).select_related(
            'category',
            'added_by'
        ).prefetch_related(
            'authors',
            'publicationauthor_set',
            'publicationauthor_set__author'
        )

        # Handle search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__first_name__icontains=search_query) |
                Q(authors__last_name__icontains=search_query)
            ).distinct()

        # Handle status filter
        status = self.request.GET.get('status')
        if status and status != 'any':
            queryset = queryset.filter(status=status)

        # Handle category filter
        category = self.request.GET.get('category')
        if category and category != 'any':
            queryset = queryset.filter(category_id=category)

        # Handle sorting
        sort_order = self.request.GET.get('order', 'desc')
        queryset = queryset.order_by(
            '-created_at' if sort_order == 'desc' else 'created_at'
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'current_section': 'submissions',
            'categories': PublicationCategory.objects.all(),
            'status_choices': [
                {'value': 'draft', 'label': 'Draft'},
                {'value': 'archived', 'label': 'Archived'},
            ]
        })
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_section'] = 'submissions'
        return context