# Generated by Django 4.2.4 on 2024-01-10 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0105_alter_innovation_image'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='innovation',
            unique_together=set(),
        ),
    ]
