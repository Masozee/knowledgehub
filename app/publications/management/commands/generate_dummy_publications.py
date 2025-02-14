# app/publications/management/commands/generate_dummy_publications.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings
from faker import Faker
from datetime import datetime, timedelta
import random
from app.people.models import Person
from app.publications.models import (
    PublicationCategory,
    Publication,
    PublicationAuthor,
    PublicationTrackingEvent
)

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Generates dummy data for publications app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--publications',
            type=int,
            default=10,
            help='Number of publications to create'
        )

    def generate_dummy_image(self):
        """Generate a dummy image file"""
        from PIL import Image
        import io

        # Create a colored rectangle
        img = Image.new('RGB', (800, 600), color=fake.hex_color())
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')

        return ContentFile(img_io.getvalue(), name=f'dummy_{fake.uuid4()}.jpg')

    def create_categories(self):
        """Create publication categories"""
        categories = [
            "Research Papers",
            "Policy Briefs",
            "Annual Reports",
            "Working Papers",
            "Technical Reports"
        ]

        created_categories = []
        for cat_name in categories:
            cat, created = PublicationCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': fake.paragraph(),
                    'background': self.generate_dummy_image()
                }
            )
            created_categories.append(cat)

        return created_categories

    def create_dummy_file(self):
        """Create a dummy PDF file"""
        content = f"Dummy Publication Content\n{fake.text()}"
        return ContentFile(content.encode(), name=f'publication_{fake.uuid4()}.pdf')

    def generate_tracking_events(self, publication):
        """Generate random tracking events for a publication"""
        # Generate events for the last 30 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        # Generate between 10 and 100 events
        num_events = random.randint(10, 100)

        for _ in range(num_events):
            event_type = random.choice(['view', 'download'])
            timestamp = fake.date_time_between(start_date=start_date, end_date=end_date)

            PublicationTrackingEvent.objects.create(
                publication=publication,
                event_type=event_type,
                timestamp=timestamp,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent()
            )

    def handle(self, *args, **options):
        self.stdout.write('Starting to generate dummy publication data...')

        # Create categories
        categories = self.create_categories()
        self.stdout.write(f'Created {len(categories)} categories')

        # Ensure we have some persons in the database
        if not Person.objects.exists():
            for _ in range(20):
                Person.objects.create(
                    name=fake.name(),
                    email=fake.email(),
                    bio=fake.text()
                )

        persons = list(Person.objects.all())

        # Create publications
        num_publications = options['publications']
        for i in range(num_publications):
            # Create publication
            pub = Publication.objects.create(
                title=fake.catch_phrase(),
                date_publish=fake.date_this_decade(),
                category=random.choice(categories),
                description=fake.text(max_nb_chars=1000),
                image=self.generate_dummy_image(),
                cover=self.generate_dummy_image(),
                file=self.create_dummy_file(),
                status=random.choice(['draft', 'published', 'archived']),
                publish=random.choice([True, False]),
                highlight=random.choice([True, False])
            )

            # Add authors (between 1 and 5 authors)
            num_authors = random.randint(1, 5)
            selected_authors = random.sample(persons, num_authors)

            for idx, author in enumerate(selected_authors):
                PublicationAuthor.objects.create(
                    publication=pub,
                    author=author,
                    order=idx,
                    is_corresponding=(idx == 0),  # First author is corresponding
                    affiliation=fake.company()
                )

            # Add editors and partners
            pub.editor.set(random.sample(persons, random.randint(1, 3)))
            pub.partners.set(random.sample(persons, random.randint(1, 3)))

            # Generate tracking events
            self.generate_tracking_events(pub)

            # Update publication stats
            pub.current_stats.update_stats()

            self.stdout.write(f'Created publication {i + 1}/{num_publications}')

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy publication data'))

# Usage:
# python manage.py generate_dummy_publications --publications 20