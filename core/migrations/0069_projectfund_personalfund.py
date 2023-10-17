# Generated by Django 4.2.4 on 2023-10-17 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_remove_innovator_account_balance'),
        ('core', '0068_transaction_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectFund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_balance', models.PositiveIntegerField(blank=True, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.project')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalFund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_balance', models.PositiveIntegerField(blank=True, null=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.innovator')),
            ],
        ),
    ]
