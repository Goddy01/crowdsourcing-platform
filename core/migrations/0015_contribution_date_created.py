# Generated by Django 4.2.4 on 2023-09-16 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_project_approved_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='contribution',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
