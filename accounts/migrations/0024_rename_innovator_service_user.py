# Generated by Django 4.2.4 on 2023-09-16 04:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_alter_baseuser_about_me'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='innovator',
            new_name='user',
        ),
    ]