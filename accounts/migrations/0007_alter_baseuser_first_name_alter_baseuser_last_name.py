# Generated by Django 4.2.3 on 2023-07-20 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_baseuser_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='first_name',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='last_name',
            field=models.CharField(max_length=256, null=True),
        ),
    ]