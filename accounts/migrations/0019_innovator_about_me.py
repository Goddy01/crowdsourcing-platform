# Generated by Django 4.2.4 on 2023-09-09 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_rename_services_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='innovator',
            name='about_me',
            field=models.TextField(blank=True, null=True),
        ),
    ]