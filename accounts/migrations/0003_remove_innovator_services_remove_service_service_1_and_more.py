# Generated by Django 4.2.4 on 2023-08-10 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_innovator_downvotes_received_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='innovator',
            name='services',
        ),
        migrations.RemoveField(
            model_name='service',
            name='service_1',
        ),
        migrations.RemoveField(
            model_name='service',
            name='service_2',
        ),
        migrations.RemoveField(
            model_name='service',
            name='service_3',
        ),
        migrations.RemoveField(
            model_name='service',
            name='service_4',
        ),
        migrations.RemoveField(
            model_name='service',
            name='service_5',
        ),
        migrations.AddField(
            model_name='innovator',
            name='service_1',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='innovator',
            name='service_2',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='innovator',
            name='service_3',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='innovator',
            name='service_4',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='innovator',
            name='service_5',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
