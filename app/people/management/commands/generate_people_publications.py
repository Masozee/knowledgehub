# people/management/commands/generate_dummy_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from app.people.models import CustomUser, Person, Organization, Relationship, Staff, PhotoBackup, Photo
import random

class Command(BaseCommand):
    help = 'Generates dummy data for Person and related models'

    def handle(self, *args, **kwargs):
        # Define first and last names
        first_names = ['Adi', 'Siti', 'Budi', 'Dewi', 'Agus', 'Ratna', 'Wawan', 'Fitri', 'Eko']
        last_names = ['Santoso', 'Wijaya', 'Siregar', 'Nugroho', 'Hidayat', 'Pratama', 'Kurniawan', 'Putri']

        # Create organizations
        organizations = [
            Organization.objects.create(name=f"Org {i}", slug=f"org-{i}", publish=True)
            for i in range(1, 4)
        ]

        # Create users and persons
        for i in range(10):  # Create 10 dummy persons
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"

            user = CustomUser.objects.create(
                email=email,
                user_type=random.choice(['staff', 'visitor', 'researcher', 'speaker', 'writer', 'partner']),
                is_email_verified=True
            )

            person = Person.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=f"0812345678{i}",
                address=f"Address {i}"
            )
            person.organization.set(random.sample(organizations, k=random.randint(1, 2)))

            # Create relationships
            related_person = random.choice(Person.objects.exclude(id=person.id))
            Relationship.objects.create(
                person=person,
                related_person=related_person,
                relationship_type=random.choice(['spouse', 'parent', 'child', 'sibling']),
                kontak_darurat=random.choice([True, False])
            )

            # Create staff if user is staff
            if user.user_type == 'staff':
                Staff.objects.create(
                    person=person,
                    employee_id=f"EMP{random.randint(1000, 9999)}",
                    department=random.choice(['HR', 'IT', 'Finance', 'Marketing']),
                    position=random.choice(['Manager', 'Developer', 'Analyst', 'Designer']),
                    hire_date=timezone.now()
                )

            # Create photo backups and photos
            backup = PhotoBackup.objects.create(
                user=user,
                status=random.choice(['pending', 'processing', 'completed', 'failed']),
                total_photos=random.randint(1, 10),
                photos_limit=random.randint(10, 20),
                initiated_by=user
            )
            for j in range(backup.total_photos):
                Photo.objects.create(
                    backup=backup,
                    google_photo_id=f"photo_{j}_{backup.id}",
                    filename=f"photo_{j}.jpg",
                    original_url=f"https://example.com/photo_{j}.jpg",
                    mime_type="image/jpeg",
                    created_time=timezone.now(),
                    photo_file=f"photo_backups/2023/10/10/photo_{j}.jpg"
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))