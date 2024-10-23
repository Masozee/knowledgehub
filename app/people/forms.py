from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.socialaccount.forms import SignupForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='visitor',
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'user_type', 'password1', 'password2')
        exclude = ('username',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'user_type')
        exclude = ('username',)

class SocialAccountSignupForm(SignupForm):
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='visitor',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def save(self, request):
        user = super().save(request)
        user.user_type = self.cleaned_data['user_type']
        user.save()
        return user