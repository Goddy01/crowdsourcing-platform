# Generated by Django 4.2.4 on 2023-09-09 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_alter_innovator_about_me'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='innovator',
            name='service_1',
        ),
        migrations.RemoveField(
            model_name='innovator',
            name='service_2',
        ),
        migrations.RemoveField(
            model_name='innovator',
            name='service_3',
        ),
        migrations.RemoveField(
            model_name='innovator',
            name='service_4',
        ),
        migrations.RemoveField(
            model_name='innovator',
            name='service_5',
        ),
    ]
