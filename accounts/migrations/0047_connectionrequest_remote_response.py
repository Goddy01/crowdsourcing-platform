# Generated by Django 4.2.4 on 2023-11-17 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0046_connectionrequest_are_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectionrequest',
            name='remote_response',
            field=models.BooleanField(default=False),
        ),
    ]
