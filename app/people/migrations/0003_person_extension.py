# Generated by Django 5.1.1 on 2025-01-10 06:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0002_remove_writer_organization_remove_writer_person_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="extension",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
