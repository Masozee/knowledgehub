from django import forms
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()


class ProjectCreateForm(forms.ModelForm):
    """
    Combined form for project creation with all fields
    """
    # Basic Info Fields
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter project title'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Write Project Description',
            'rows': 3
        })
    )
    public_project = forms.BooleanField(
        required=False,
        initial=False,
        label='Public Project'
    )

    # Team Members Field
    team_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom-control-input'}),
        required=False,
        help_text='Select team members for this project'
    )

    # Project Lead
    project_lead = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select js-select2',
            'data-placeholder': 'Select Project Lead'
        }),
        required=True,
        label='Project Lead'
    )

    # Additional Details
    client = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Client or Company name'
        }),
        required=True
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control date-picker',
            'placeholder': 'mm/dd/yyyy'
        }),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control date-picker',
            'placeholder': 'mm/dd/yyyy'
        }),
        required=True
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control js-tagify',
            'placeholder': 'Add Tags'
        })
    )

    # Optional Settings
    follow_project = forms.BooleanField(required=False, initial=True)
    save_project = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'public_project',
            'start_date', 'end_date'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Exclude current user from team members selection
            self.fields['team_members'].queryset = User.objects.filter(
                is_active=True
            ).exclude(
                id=self.user.id
            ).order_by('first_name')

            # Set initial project lead as current user
            self.fields['project_lead'].initial = self.user.id

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError({
                'end_date': 'End date cannot be earlier than start date'
            })

        return cleaned_data

    def save(self, commit=True):
        project = super().save(commit=False)
        if self.user:
            project.created_by = self.user

        if commit:
            project.save()

            # Add project lead as team member with manager role
            project_lead = self.cleaned_data.get('project_lead')
            if project_lead:
                ProjectMember.objects.create(
                    project=project,
                    user=project_lead,
                    role='manager'
                )

            # Add team members
            team_members = self.cleaned_data.get('team_members', [])
            for member in team_members:
                if member != project_lead:  # Don't duplicate project lead
                    ProjectMember.objects.create(
                        project=project,
                        user=member,
                        role='member'
                    )

        return project