# Generated by Django 4.2.4 on 2023-08-10 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_innovator_services_remove_service_service_1_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Service',
        ),
    ]