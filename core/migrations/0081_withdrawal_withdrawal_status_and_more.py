# Generated by Django 4.2.4 on 2023-11-02 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0080_withdrawal_approved_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawal',
            name='withdrawal_status',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='withdrawprojectfunds',
            name='withdrawal_status',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]