# Generated by Django 4.2.4 on 2023-09-20 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_remove_investment_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='amount_left',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=255, null=True),
        ),
    ]