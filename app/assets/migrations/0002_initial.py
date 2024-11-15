# Generated by Django 5.1.1 on 2024-10-15 06:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assets', '0001_initial'),
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='category',
            field=models.ForeignKey(limit_choices_to={'category': '1'}, on_delete=django.db.models.deletion.CASCADE, to='config.option'),
        ),
        migrations.AddField(
            model_name='asset',
            name='status',
            field=models.ForeignKey(limit_choices_to={'category': '2'}, on_delete=django.db.models.deletion.CASCADE, related_name='asset_status', to='config.option'),
        ),
        migrations.AddField(
            model_name='assetassignment',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='assets.asset'),
        ),
    ]
