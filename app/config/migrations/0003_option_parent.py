# Generated by Django 5.1.1 on 2024-10-09 05:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_alter_option_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='config.option', verbose_name='Parent'),
        ),
    ]
