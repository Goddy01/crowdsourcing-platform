# Generated by Django 4.2.4 on 2023-12-15 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0091_alter_project_fund_raised'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='fund_raised',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=255, null=True),
        ),
    ]
