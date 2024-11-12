# forms.py
from django import forms


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