# Generated by Django 4.2.4 on 2024-01-10 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0103_alter_innovation_downvotes_alter_innovation_upvotes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='innovation',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
