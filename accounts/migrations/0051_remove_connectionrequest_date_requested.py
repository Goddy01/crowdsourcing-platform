# Generated by Django 4.2.4 on 2023-11-18 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0050_connection_conn_request'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='connectionrequest',
            name='date_requested',
        ),
    ]
