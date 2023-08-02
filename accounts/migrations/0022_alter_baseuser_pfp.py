# Generated by Django 4.2.3 on 2023-08-02 14:03

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_alter_baseuser_pfp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='pfp',
            field=models.ImageField(blank=True, default='default_profile_image.jpg', null=True, upload_to=accounts.models.upload_location_pfp),
        ),
    ]
