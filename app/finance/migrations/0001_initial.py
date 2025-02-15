# Generated by Django 5.1.1 on 2024-12-28 16:15

import app.finance.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=3, unique=True)),
                ("name", models.CharField(max_length=50)),
                ("symbol", models.CharField(max_length=5)),
            ],
            options={
                "verbose_name_plural": "Currencies",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="Donor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("contact_person", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=50)),
                ("address", models.TextField()),
                ("notes", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="FiscalYear",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("year", models.IntegerField(unique=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_active", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-year"],
            },
        ),
        migrations.CreateModel(
            name="CostCenter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="finance.costcenter",
                    ),
                ),
            ],
            options={
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="Budget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "initial_amount",
                    app.finance.models.MoneyField(decimal_places=2, max_digits=15),
                ),
                (
                    "revised_amount",
                    app.finance.models.MoneyField(
                        decimal_places=2, default=0, max_digits=15
                    ),
                ),
                (
                    "budget_type",
                    models.CharField(
                        choices=[
                            ("OPERATIONAL", "Operational"),
                            ("CAPITAL", "Capital"),
                            ("PROJECT", "Project"),
                            ("EMERGENCY", "Emergency Fund"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="finance.currency",
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="finance.fiscalyear",
                    ),
                ),
            ],
            options={
                "ordering": ["-fiscal_year"],
                "unique_together": {("fiscal_year", "budget_type")},
            },
        ),
        migrations.CreateModel(
            name="BudgetLine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    app.finance.models.MoneyField(decimal_places=2, max_digits=15),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "budget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="allocations",
                        to="finance.budget",
                    ),
                ),
                (
                    "cost_center",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="finance.costcenter",
                    ),
                ),
            ],
            options={
                "ordering": ["cost_center"],
                "unique_together": {("budget", "cost_center")},
            },
        ),
        migrations.CreateModel(
            name="ExchangeRate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("rate", models.DecimalField(decimal_places=6, max_digits=12)),
                ("date", models.DateField()),
                (
                    "from_currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="from_rates",
                        to="finance.currency",
                    ),
                ),
                (
                    "to_currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="to_rates",
                        to="finance.currency",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "indexes": [
                    models.Index(
                        fields=["date", "from_currency", "to_currency"],
                        name="finance_exc_date_475979_idx",
                    )
                ],
                "unique_together": {("from_currency", "to_currency", "date")},
            },
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("description", models.TextField()),
                (
                    "amount",
                    app.finance.models.MoneyField(decimal_places=2, max_digits=15),
                ),
                (
                    "expense_type",
                    models.CharField(
                        choices=[
                            ("DIRECT", "Direct Cost"),
                            ("INDIRECT", "Indirect Cost"),
                            ("OVERHEAD", "Overhead"),
                        ],
                        max_length=20,
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("SUBMITTED", "Submitted"),
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                            ("PAID", "Paid"),
                        ],
                        default="DRAFT",
                        max_length=20,
                    ),
                ),
                ("submitted_date", models.DateTimeField(blank=True, null=True)),
                ("approved_date", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approved_expenses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "cost_center",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="finance.costcenter",
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="finance.currency",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="submitted_expenses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "indexes": [
                    models.Index(
                        fields=["status", "date"], name="finance_exp_status_f5c3db_idx"
                    ),
                    models.Index(
                        fields=["content_type", "object_id"],
                        name="finance_exp_content_93b76f_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Grant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "grant_type",
                    models.CharField(
                        choices=[
                            ("RESTRICTED", "Restricted"),
                            ("UNRESTRICTED", "Unrestricted"),
                            ("PROJECT", "Project-Based"),
                            ("PROGRAM", "Program-Based"),
                        ],
                        max_length=20,
                    ),
                ),
                ("reference_number", models.CharField(max_length=50, unique=True)),
                (
                    "amount",
                    app.finance.models.MoneyField(decimal_places=2, max_digits=15),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "reporting_frequency",
                    models.CharField(
                        choices=[
                            ("MONTHLY", "Monthly"),
                            ("QUARTERLY", "Quarterly"),
                            ("SEMI_ANNUAL", "Semi-Annual"),
                            ("ANNUAL", "Annual"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="finance.currency",
                    ),
                ),
                (
                    "donor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="finance.donor"
                    ),
                ),
            ],
            options={
                "ordering": ["-start_date"],
                "indexes": [
                    models.Index(
                        fields=["grant_type", "start_date"],
                        name="finance_gra_grant_t_486df8_idx",
                    ),
                    models.Index(
                        fields=["donor", "reference_number"],
                        name="finance_gra_donor_i_92963f_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="SupportingDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to="financial_documents/%Y/%m/")),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("INVOICE", "Invoice"),
                            ("RECEIPT", "Receipt"),
                            ("CONTRACT", "Contract"),
                            ("REPORT", "Financial Report"),
                            ("OTHER", "Other Documentation"),
                        ],
                        max_length=20,
                    ),
                ),
                ("document_number", models.CharField(blank=True, max_length=50)),
                ("document_date", models.DateField()),
                ("upload_date", models.DateTimeField(auto_now_add=True)),
                ("description", models.TextField()),
                ("object_id", models.PositiveIntegerField()),
                ("verification_date", models.DateTimeField(blank=True, null=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-document_date"],
                "indexes": [
                    models.Index(
                        fields=["document_type", "document_date"],
                        name="finance_sup_documen_dbfdb4_idx",
                    ),
                    models.Index(
                        fields=["content_type", "object_id"],
                        name="finance_sup_content_3e23d3_idx",
                    ),
                ],
            },
        ),
    ]
