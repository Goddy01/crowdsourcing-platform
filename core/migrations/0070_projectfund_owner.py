# Generated by Django 4.2.4 on 2023-10-17 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_innovator_owner_funds'),
        ('core', '0069_projectfund_personalfund'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectfund',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.innovator'),
        ),
    ]
