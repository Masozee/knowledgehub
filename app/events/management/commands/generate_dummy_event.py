# events/management/commands/generate_event_dummy_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.people.models import Person, CustomUser
from app.project.models import Project
from app.events.models import EventCategory, Event, Speaker, SpeakerAttachment
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates dummy data for Event and related models'

    def handle(self, *args, **kwargs):
        # Get existing users or create new ones if none exist
        users = User.objects.all()
        if not users.exists():
            for i in range(5):
                user = User.objects.create(
                    email=f"user{i}@example.com",
                    first_name=f"User{i}",
                    last_name="Doe",
                    is_email_verified=True
                )
                users.append(user)

        # Get existing persons (speakers) or create new ones if none exist
        persons = Person.objects.all()
        if not persons.exists():
            for i in range(10):
                person = Person.objects.create(
                    first_name=f"Person{i}",
                    last_name="Smith",
                    email=f"person{i}@example.com",
                    phone_number=f"0812345678{i}",
                    address=f"Address {i}"
                )
                persons.append(person)

        # Create projects (optional, for linking to events)
        projects = []
        for i in range(3):
            project = Project.objects.create(
                title=f"Project {i + 1}",
                description=f"Description for Project {i + 1}",
                status=random.choice(['planning', 'active', 'on_hold', 'completed', 'cancelled']),
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=random.randint(30, 365)),
                public_project=random.choice([True, False]),
                created_by=random.choice(users)
            )
            projects.append(project)

        # Create event categories
        categories = []
        for i in range(3):
            category = EventCategory.objects.create(
                name=f"Category {i + 1}",
                description=f"Description for Category {i + 1}"
            )
            categories.append(category)

        # Create events
        events = []
        for i in range(5):
            event = Event.objects.create(
                title=f"Event {i + 1}",
                slug=f"event-{i + 1}",
                description=f"Description for Event {i + 1}",
                category=random.choice(categories),
                organizer=random.choice(users),
                start_date=timezone.now() + timedelta(days=random.randint(1, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(31, 60)),
                location=f"Location {i + 1}",
                venue_name=f"Venue {i + 1}",
                address=f"Address {i + 1}",
                register=f"https://example.com/register/{i + 1}",
                youtube=f"https://youtube.com/event{i + 1}",
                project=random.choice(projects) if projects else None,
                status=random.choice(['draft', 'published', 'cancelled', 'completed']),
                max_capacity=random.randint(50, 200),
                current_capacity=random.randint(0, 50)
            )
            events.append(event)

        # Create speakers
        speakers = []
        for event in events:
            for i in range(3):
                speaker = Speaker.objects.create(
                    person=random.choice(persons),
                    event=event,
                    speaker_type=random.choice(['keynote', 'guest', 'panelist', 'moderator']),
                    presentation_title=f"Presentation {i + 1} for {event.title}",
                    presentation_description=f"Description for Presentation {i + 1}",
                    speaking_slot_start=event.start_date + timedelta(hours=random.randint(1, 3)),
                    speaking_slot_end=event.start_date + timedelta(hours=random.randint(4, 6)),
                    order=i + 1,
                    is_featured=random.choice([True, False])
                )
                speakers.append(speaker)

        # Create speaker attachments
        for speaker in speakers:
            for i in range(2):
                SpeakerAttachment.objects.create(
                    speaker=speaker,
                    title=f"Attachment {i + 1} for {speaker.presentation_title}",
                    description=f"Description for Attachment {i + 1}",
                    attachment_type=random.choice(['presentation', 'handout', 'supplementary']),
                    file=f"events/speaker_attachments/sample_file_{i + 1}.pdf",
                    is_public=random.choice([True, False])
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data for Event and related models!'))