# Generated by Django 4.2.4 on 2023-11-08 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0088_projectmilestone_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmilestone',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]