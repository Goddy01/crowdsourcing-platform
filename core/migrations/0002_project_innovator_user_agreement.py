# Generated by Django 4.2.4 on 2023-09-11 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='innovator_user_agreement',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
