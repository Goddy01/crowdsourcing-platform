# Generated by Django 4.2.4 on 2023-10-17 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_delete_personalfund'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectFund',
        ),
    ]
