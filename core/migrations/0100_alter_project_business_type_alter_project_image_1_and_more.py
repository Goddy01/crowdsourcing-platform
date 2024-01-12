# Generated by Django 4.2.4 on 2024-01-10 13:47

import core.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0099_delete_testimony'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='business_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='image_1',
            field=models.ImageField(max_length=500, upload_to=core.models.upload_project_gallery),
        ),
        migrations.AlterField(
            model_name='project',
            name='image_2',
            field=models.ImageField(max_length=500, upload_to=core.models.upload_project_gallery),
        ),
        migrations.AlterField(
            model_name='project',
            name='image_3',
            field=models.ImageField(max_length=500, upload_to=core.models.upload_project_gallery),
        ),
        migrations.AlterField(
            model_name='project',
            name='video',
            field=models.FileField(max_length=500, null=True, upload_to=core.models.upload_project_gallery, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]),
        ),
    ]