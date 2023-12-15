# Generated by Django 5.0 on 2023-12-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0090_alter_make_investment_send_to_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='fund_raised',
            field=models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=255, null=True),
        ),
    ]
