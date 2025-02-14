from app.people.models import CustomUser, Organization, Person, Staff, Relationship, PhotoBackup, Photo
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import random


def generate_fake_name():
    first_names = ['Adi', 'Siti', 'Budi', 'Dewi', 'Agus', 'Ratna', 'Wawan', 'Fitri', 'Eko']
    last_names = ['Santoso', 'Wijaya', 'Siregar', 'Nugroho', 'Hidayat', 'Pratama', 'Kurniawan', 'Putri']
    return random.choice(first_names), random.choice(last_names)


def create_dummy_data():
    # Create Organizations
    organizations = []
    for i in range(8):
        org = Organization.objects.create(
            name=f"Organization {i}",
            slug=f"org-{i}",
            phone=f"+1-555-{str(i).zfill(4)}",
            address=f"{i} Main Street",
            description=f"Description for Organization {i}",
            publish=True
        )
        organizations.append(org)

    # Create 50 CustomUsers
    users = []
    user_types = ['staff', 'visitor', 'researcher', 'speaker', 'writer', 'partner']

    for i in range(50):
        first_name, last_name = generate_fake_name()
        user = CustomUser.objects.create(
            email=f"user{i}@example.com",
            password=make_password('password123'),
            first_name=first_name,
            last_name=last_name,
            user_type=random.choice(user_types),
            is_email_verified=True,
            is_active=True
        )
        users.append(user)

    # Create 100 People (50 with CustomUser, 50 without)
    people = []
    for i in range(100):
        first_name, last_name = generate_fake_name()
        person = Person.objects.create(
            user=users[i] if i < len(users) else None,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=timezone.now().date() - timedelta(days=random.randint(7300, 25550)),
            email=f"person{i}@example.com",
            phone_number=f"+1-555-{str(i).zfill(4)}",
            address=f"{i} Main Street"
        )
        person.organization.add(random.choice(organizations))
        people.append(person)

    # Create Staff (25 members)
    departments = ['IT', 'HR', 'Research', 'Marketing', 'Sales']
    positions = ['Manager', 'Director', 'Coordinator', 'Specialist', 'Analyst']

    for i in range(25):
        Staff.objects.create(
            person=people[i],
            employee_id=f"EMP{str(i).zfill(4)}",
            department=random.choice(departments),
            position=random.choice(positions),
            hire_date=timezone.now().date() - timedelta(days=random.randint(0, 3650))
        )

    # Create Relationships
    relationship_types = ['spouse', 'parent', 'child', 'sibling']
    for i in range(50):
        person1 = random.choice(people)
        person2 = random.choice([p for p in people if p != person1])
        Relationship.objects.create(
            person=person1,
            related_person=person2,
            relationship_type=random.choice(relationship_types),
            kontak_darurat=random.choice([True, False])
        )


if __name__ == '__main__':
    create_dummy_data()