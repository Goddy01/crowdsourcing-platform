# Generated by Django 4.2.4 on 2023-11-27 18:26

import chat.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_chat_is_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='file_content',
            field=models.FileField(blank=True, null=True, upload_to=chat.models.upload_in_chat_files),
        ),
    ]
