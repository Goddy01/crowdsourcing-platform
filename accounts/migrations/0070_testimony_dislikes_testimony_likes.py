# Generated by Django 4.2.4 on 2024-01-05 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0069_alter_testimony_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='testimony',
            name='dislikes',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='testimony',
            name='likes',
            field=models.IntegerField(null=True),
        ),
    ]
