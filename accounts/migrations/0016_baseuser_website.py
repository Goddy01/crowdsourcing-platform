# Generated by Django 4.2.3 on 2023-07-31 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_baseuser_zipcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='website',
            field=models.URLField(default='https://company.com/'),
        ),
    ]