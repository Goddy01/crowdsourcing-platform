# Generated by Django 4.2.4 on 2023-10-14 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_sendmoney'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='post_balance',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='pre_balance',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
