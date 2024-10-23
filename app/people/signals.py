from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=SocialAccount)
def social_account_created(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        provider = instance.provider

        # Update OAuth information
        user.oauth_provider = provider
        if provider == 'google':
            token = instance.socialtoken_set.first()
            if token:
                user.oauth_token = token.token
                user.oauth_refresh_token = token.token_secret
                user.oauth_token_expiry = token.expires_at

        user.save()