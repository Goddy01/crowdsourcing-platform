# Generated by Django 4.2.4 on 2023-09-08 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_innovatorskill_skill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='innovatorskill',
            name='skill',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
