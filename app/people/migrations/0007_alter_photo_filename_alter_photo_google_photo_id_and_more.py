# Generated by Django 5.1.1 on 2024-10-22 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_alter_photobackup_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='filename',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='photo',
            name='google_photo_id',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='photo',
            name='original_url',
            field=models.TextField(),
        ),
    ]