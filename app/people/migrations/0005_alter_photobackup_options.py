# Generated by Django 5.1.1 on 2024-10-22 08:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_photobackup_delete_backupzip'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photobackup',
            options={'ordering': ['-created_at'], 'verbose_name': 'Backup', 'verbose_name_plural': 'Backups'},
        ),
    ]
