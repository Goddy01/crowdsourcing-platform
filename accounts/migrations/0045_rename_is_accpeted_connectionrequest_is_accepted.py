# Generated by Django 4.2.4 on 2023-11-16 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0044_connectionrequest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='connectionrequest',
            old_name='is_accpeted',
            new_name='is_accepted',
        ),
    ]