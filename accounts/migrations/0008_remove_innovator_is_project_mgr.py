# Generated by Django 4.2.4 on 2023-09-07 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_innovator_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='innovator',
            name='is_project_mgr',
        ),
    ]