# Generated by Django 4.2.4 on 2023-10-04 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_make_investment_reference_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(blank=True, default='YET TO BE REVIEWED', max_length=255, null=True),
        ),
    ]
