# Generated by Django 4.2.4 on 2023-10-17 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_innovator_owner_funds'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='innovator',
            name='owner_funds',
        ),
        migrations.AddField(
            model_name='innovator',
            name='personal_funds',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
