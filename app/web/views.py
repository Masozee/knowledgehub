# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.people.models import *
from app.project.models import *
from django.views.generic import ListView
from django.db.models import Exists, OuterRef, Q
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required(login_url='/accounts/login/')
def index(request):
    try:
        user = CustomUser.objects.get(email=request.user.email)
        context = {
            'user': user,
            'user_type': user.user_type,  # Since you have a user_type field
            'is_verified': user.is_email_verified,
        }
        return render(request, 'dashboard/index.html', context)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')
#homepage ==========================================================================================================================================================
@login_required
def userHome(request):
    return render(request, 'dashboard/user/index.html')


#project ==========================================================================================================================================================
def projectList(request):
    return render(request, 'dashboard/project/index.html')

def projectDetail(request):
    return render(request, 'dashboard/project/detail.html')


def calendar(request):
    return render(request, 'dashboard/events/calendar.html')

@login_required
def wiki(request):
    return render(request, 'dashboard/wiki/index.html')

@login_required
def srm(request):
    return render(request, 'dashboard/srm/index.html')

@login_required
def assetList(request):
    return render(request, 'dashboard/asset/index.html')

@login_required
def chatAI(request):
    return render(request, 'dashboard/ai/index.html')


class StakeholderManagementView(LoginRequiredMixin, ListView):
    model = Person
    template_name = 'dashboard/srm/index.html'
    context_object_name = 'stakeholders'
    paginate_by = 10

    def get_queryset(self):
        # Create a subquery to check for relationships
        has_relationship = Relationship.objects.filter(
            person=OuterRef('pk')
        ).values('pk')

        # Get search query
        search_query = self.request.GET.get('search', '')

        # Base queryset with relationship annotation
        queryset = Person.objects.annotate(
            has_relationship=Exists(has_relationship)
        )

        # Apply search if provided
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(organization__name__icontains=search_query)
            )

        # Order by name
        queryset = queryset.order_by('first_name', 'last_name')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add total count
        context['total_stakeholders'] = Person.objects.count()

        # Get staff information for each person
        staff_dict = {
            staff.person_id: staff
            for staff in Staff.objects.select_related('person')
        }

        # Enhance stakeholder data with staff info and status
        for stakeholder in context['stakeholders']:
            stakeholder.staff_info = staff_dict.get(stakeholder.id)
            if hasattr(stakeholder, 'has_relationship') and stakeholder.has_relationship:
                stakeholder.status = 'Active'
                stakeholder.status_class = 'success'
            else:
                stakeholder.status = 'No Relationship'
                stakeholder.status_class = 'warning'

        # Add organizations for filtering
        context['organizations'] = Organization.objects.all()

        return context