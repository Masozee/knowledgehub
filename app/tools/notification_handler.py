from django.contrib.auth import get_user_model
from django.apps import apps
from .models import Notification

User = get_user_model()


def create_notification(sender, instance, created, **kwargs):
    if sender in [
        apps.get_model('publications', 'Publication'),
        apps.get_model('publications', 'Bulletin'),
        apps.get_model('publications', 'News'),
        apps.get_model('events', 'Event')
    ]:
        action = 'created' if created else 'updated'
        message = f"A new {sender.__name__.lower()} has been {action}: {instance.title}"

        # Assuming you want to notify all users
        for user in User.objects.all():
            Notification.objects.create(
                user=user,
                content_object=instance,
                message=message
            )