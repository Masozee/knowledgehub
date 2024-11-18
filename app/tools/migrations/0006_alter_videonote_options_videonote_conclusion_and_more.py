# Generated by Django 5.1.1 on 2024-11-12 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0005_videocontent_transcript_json_path_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='videonote',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='videonote',
            name='conclusion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='videonote',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='videonote',
            name='summary',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='videonote',
            name='video',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tools.videocontent'),
        ),
    ]