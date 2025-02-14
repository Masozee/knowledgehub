from django import forms
from django.forms import inlineformset_factory
from .models import Publication, PublicationAuthor

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = [
            'title', 'category', 'project', 'description',
            'date_publish', 'file', 'image', 'cover',
            'image_credit', 'topic', 'tags', 'status',
            'publish', 'highlight'
        ]
        widgets = {
            'date_publish': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'data-role': 'tagsinput'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

PublicationAuthorFormSet = inlineformset_factory(
    Publication,
    PublicationAuthor,
    fields=('author', 'order', 'is_corresponding', 'affiliation'),
    extra=1,
    can_delete=True
)

class PublicationSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search publications...',
        })
    )