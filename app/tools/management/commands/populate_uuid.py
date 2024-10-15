from django.core.management.base import BaseCommand
from app.tools.models import Conversation  # adjust the import path as needed
import uuid

class Command(BaseCommand):
    help = 'Populates empty uuid fields in Conversation model'

    def handle(self, *args, **kwargs):
        conversations = Conversation.objects.filter(uuid__isnull=True)
        for conversation in conversations:
            conversation.uuid = uuid.uuid4()
            conversation.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully populated {conversations.count()} conversations with UUIDs'))
