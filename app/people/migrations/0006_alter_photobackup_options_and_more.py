# Generated by Django 5.1.1 on 2024-10-22 15:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_alter_photobackup_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photobackup',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='photobackup',
            name='zip_file',
        ),
        migrations.AddField(
            model_name='photobackup',
            name='photos_limit',
            field=models.IntegerField(default=50, help_text='Number of photos to backup (0 for unlimited)'),
        ),
        migrations.AddField(
            model_name='photobackup',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='photobackup',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='photobackup',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('google_photo_id', models.CharField(max_length=255)),
                ('filename', models.CharField(max_length=255)),
                ('original_url', models.URLField()),
                ('mime_type', models.CharField(max_length=100)),
                ('created_time', models.DateTimeField(blank=True, null=True)),
                ('downloaded_at', models.DateTimeField(auto_now_add=True)),
                ('photo_file', models.FileField(upload_to='photo_backups/%Y/%m/%d/')),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('backup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='people.photobackup')),
            ],
            options={
                'unique_together': {('backup', 'google_photo_id')},
            },
        ),
    ]