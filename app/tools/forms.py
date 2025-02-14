# forms.py
from django import forms
from app.people.models import *
from app.tools.models import *

class VideoUploadForm(forms.Form):
    video_type = forms.ChoiceField(
        choices=[('youtube', 'YouTube URL'), ('local', 'Local File')],
        widget=forms.RadioSelect(attrs={
            'class': 'custom-control-input'
        })
    )

    youtube_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter YouTube URL'
        })
    )

    video_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'custom-file-input',
            'accept': 'video/mp4,video/avi,video/mov'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        video_type = cleaned_data.get('video_type')
        youtube_url = cleaned_data.get('youtube_url')
        video_file = cleaned_data.get('video_file')

        if video_type == 'youtube' and not youtube_url:
            raise forms.ValidationError('Please provide a YouTube URL')
        elif video_type == 'local' and not video_file:
            raise forms.ValidationError('Please upload a video file')

        return cleaned_data

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = [
            'title', 'description', 'request_type',
            'priority', 'attachments', 'tags', 'project'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.CheckboxSelectMultiple()
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = SupportComment
        fields = ['content', 'attachment', 'internal_note']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

class AssignmentForm(forms.Form):
    staff_member = forms.ModelChoiceField(
        queryset=Staff.objects.filter(is_active=True)
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)

class ResolutionForm(forms.Form):
    resolution_notes = forms.CharField(widget=forms.Textarea)
    satisfaction_rating = forms.IntegerField(
        min_value=1, max_value=5,
        required=False,
        widget=forms.RadioSelect(choices=[
            (i, f"{i} stars") for i in range(1, 6)
        ])
    )