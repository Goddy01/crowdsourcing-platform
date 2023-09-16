# Generated by Django 4.2.4 on 2023-09-16 09:53

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_contribution_date_created'),
    ]

    operations = [
        migrations.RenameField(
            model_name='innovation',
            old_name='contribution',
            new_name='contributions',
        ),
        migrations.AlterField(
            model_name='innovation',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.upload_project_gallery),
        ),
    ]
