# Generated by Django 5.1.1 on 2024-10-23 07:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('finance', '0004_currency_alter_budget_additional_amount_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='budget',
            options={'ordering': ['-fiscal_year']},
        ),
        migrations.AlterModelOptions(
            name='budgetallocation',
            options={'ordering': ['category']},
        ),
        migrations.AlterModelOptions(
            name='currency',
            options={'ordering': ['code'], 'verbose_name_plural': 'Currencies'},
        ),
        migrations.AlterModelOptions(
            name='documentproof',
            options={'ordering': ['-upload_date']},
        ),
        migrations.AlterModelOptions(
            name='exchangerate',
            options={'ordering': ['-date', 'from_currency', 'to_currency']},
        ),
        migrations.AlterModelOptions(
            name='grant',
            options={'ordering': ['-start_date']},
        ),
        migrations.AlterModelOptions(
            name='grantexpense',
            options={'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='journalentry',
            options={'ordering': ['-date'], 'verbose_name_plural': 'Journal entries'},
        ),
        migrations.AlterModelOptions(
            name='posallocation',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='posexpense',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='budgetallocation',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.currency'),
        ),
        migrations.AddField(
            model_name='posallocation',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='posallocation',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grantexpense',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.currency'),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.currency'),
        ),
        migrations.AlterField(
            model_name='posexpense',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.currency'),
        ),
    ]
