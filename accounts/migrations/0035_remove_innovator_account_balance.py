# Generated by Django 4.2.4 on 2023-10-17 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0034_alter_baseuser_website'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='innovator',
            name='account_balance',
        ),
    ]
