# app/management/commands/generate_asset_dummy_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.config.models import *
from app.assets.models import (
    Asset, Maintenance, Depreciation, Inventory,
    AssetLifecycle, Compliance, Supplier,
    Procurement, AssetAssignment
)
from datetime import date, timedelta
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Generates dummy data for Asset Management System'

    def handle(self, *args, **kwargs):
        # Create test user if not exists
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'is_active': True,
                'first_name': 'Test',
                'last_name': 'User',
                'user_type': 'staff'  # Adjust this based on your user_type choices
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created test user: {user.email}'))

        # Create categories and options
        categories_data = {
            'Asset Types': ['Laptop', 'Desktop', 'Server', 'Network Equipment', 'Furniture'],
            'Asset Status': ['Active', 'In Maintenance', 'Retired', 'Disposed'],
            'Maintenance Types': ['Preventive', 'Corrective', 'Predictive', 'Emergency']
        }

        option_configs = {}
        category_map = {}  # To map category names to IDs for asset creation

        for cat_name, options in categories_data.items():
            # Create category
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': f'Category for {cat_name.lower()}',
                    'is_active': True,
                    'created_by': user
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

            category_map[cat_name] = category
            category_options = []

            # Create options for this category
            for idx, option_name in enumerate(options):
                opt, created = Option.objects.get_or_create(
                    category=category,
                    name=option_name,
                    defaults={
                        'value': option_name.lower().replace(' ', '_'),
                        'description': f'Option for {option_name}',
                        'is_active': True,
                        'order': idx,
                        'created_by': user
                    }
                )
                category_options.append(opt)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created option: {opt.name} in category {category.name}'))

            option_configs[cat_name] = category_options

        # Create suppliers
        suppliers = []
        supplier_data = [
            ('Tech Solutions Inc', 'John Smith', '+1234567890'),
            ('Office Supplies Co', 'Jane Doe', '+0987654321'),
            ('IT Equipment Ltd', 'Bob Johnson', '+1122334455')
        ]

        for name, contact, phone in supplier_data:
            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'contact_person': contact,
                    'phone_number': phone,
                    'email': f'{contact.lower().replace(" ", ".")}@{name.lower().replace(" ", "")}.com',
                    'address': f'{random.randint(1, 999)} Business Street, Tech City'
                }
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created supplier: {supplier.name}'))

        # Create assets and related records
        for i in range(10):  # Create 10 assets
            # Create asset
            asset = Asset.objects.create(
                name=f'Asset {i + 1}',
                asset_id=f'AST{str(i + 1).zfill(3)}',
                category=random.choice(option_configs['Asset Types']),
                purchase_date=date.today() - timedelta(days=random.randint(1, 365)),
                purchase_price=Decimal(str(random.randint(1000, 5000))),
                warranty_expiration=date.today() + timedelta(days=random.randint(1, 730)),
                location=f'Floor {random.randint(1, 5)}, Room {random.randint(101, 999)}',
                current_value=Decimal(str(random.randint(500, 4000))),
                status=random.choice(option_configs['Asset Status'])
            )
            self.stdout.write(self.style.SUCCESS(f'Created asset: {asset.name}'))

            # Create maintenance records
            for _ in range(random.randint(1, 3)):
                Maintenance.objects.create(
                    asset=asset,
                    maintenance_type=random.choice(option_configs['Maintenance Types']),
                    maintenance_date=date.today() - timedelta(days=random.randint(1, 180)),
                    next_maintenance_date=date.today() + timedelta(days=random.randint(1, 180)),
                    cost=Decimal(str(random.randint(100, 500))),
                    performed_by=f'Technician {random.randint(1, 5)}',
                    remarks='Routine maintenance and inspection'
                )

            # Create depreciation record
            Depreciation.objects.create(
                asset=asset,
                depreciation_date=date.today(),
                depreciation_amount=Decimal(str(random.randint(100, 1000))),
                remaining_value=asset.current_value
            )

            # Create inventory record
            Inventory.objects.create(
                asset=asset,
                stock_quantity=random.randint(1, 10),
                reorder_threshold=random.randint(1, 5)
            )

            # Create lifecycle record
            AssetLifecycle.objects.create(
                asset=asset,
                stage=random.choice(['Acquisition', 'Deployment', 'Maintenance', 'End of Life']),
                date=asset.purchase_date,
                remarks=f'Asset lifecycle stage recorded'
            )

            # Create compliance record
            Compliance.objects.create(
                asset=asset,
                compliance_type=random.choice(['Safety', 'Environmental', 'Regulatory']),
                status=random.choice(['Compliant', 'Non-Compliant', 'Pending Review']),
                last_checked=date.today() - timedelta(days=random.randint(1, 90)),
                next_check_due=date.today() + timedelta(days=random.randint(1, 90)),
                remarks='Regular compliance check'
            )

            # Create procurement record
            Procurement.objects.create(
                asset=asset,
                supplier=random.choice(suppliers),
                procurement_date=asset.purchase_date,
                cost=asset.purchase_price,
                payment_status=random.choice(['Paid', 'Pending', 'Partially Paid'])
            )

            # Create asset assignment
            AssetAssignment.objects.create(
                asset=asset,
                user=user,
                assigned_date=date.today() - timedelta(days=random.randint(1, 30)),
                remarks='Standard asset assignment'
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated all dummy data!'))