# config/management/commands/generate_option_dummy_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.config.models import Category, Option

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates dummy data for Option model with nested subfields'

    def handle(self, *args, **kwargs):
        # Get or create the category with id=1
        category, created = Category.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Publication',
                'description': 'Category for publication types',
                'is_active': True,
                'created_by': User.objects.first()  # Assign the first user as the creator
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Using existing category: {category.name}'))

        # Define the main topics and their subfields
        main_topics = [
            {
                'name': 'Economics',
                'subfields': [
                    'Microeconomics',
                    'Macroeconomics',
                    'Behavioral Economics',
                    'Development Economics',
                    'International Trade',
                    'Public Economics',
                    'Environmental Economics',
                ]
            },
            {
                'name': 'International Relations',
                'subfields': [
                    'Global Governance',
                    'International Security',
                    'Foreign Policy',
                    'Conflict Resolution',
                    'Regional Studies',
                ]
            },
            {
                'name': 'Politics',
                'subfields': [
                    'Political Theory',
                    'Comparative Politics',
                    'Public Policy',
                    'Political Institutions',
                    'Elections',
                    'Political Communication',
                ]
            },
        ]

        # Create options under the category
        for main_topic in main_topics:
            # Create the main topic option
            main_option, created = Option.objects.get_or_create(
                category=category,
                name=main_topic['name'],
                defaults={
                    'value': main_topic['name'].lower().replace(' ', '_'),
                    'description': f'Main topic: {main_topic["name"]}',
                    'order': 0,
                    'is_active': True,
                    'created_by': User.objects.first()  # Assign the first user as the creator
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created main topic: {main_option.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Main topic already exists: {main_option.name}'))

            # Create subfield options under the main topic
            for index, subfield in enumerate(main_topic['subfields']):
                subfield_option, created = Option.objects.get_or_create(
                    category=category,
                    name=subfield,
                    defaults={
                        'value': subfield.lower().replace(' ', '_'),
                        'description': f'Subfield of {main_topic["name"]}: {subfield}',
                        'order': index + 1,
                        'is_active': True,
                        'parent': main_option,  # Link to the main topic
                        'created_by': User.objects.first()  # Assign the first user as the creator
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created subfield: {subfield_option.name} under {main_option.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Subfield already exists: {subfield_option.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data for Option model!'))