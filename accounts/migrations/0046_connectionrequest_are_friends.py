# Generated by Django 4.2.4 on 2023-11-17 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0045_rename_is_accpeted_connectionrequest_is_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectionrequest',
            name='are_friends',
            field=models.BooleanField(default=False),
        ),
    ]