# Generated by Django 4.2.4 on 2023-10-18 18:48

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0038_remove_innovator_personal_funds_and_more'),
        ('core', '0073_delete_projectfund'),
    ]

    operations = [
        migrations.CreateModel(
            name='WithdrawProjectFunds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(blank=True, null=True)),
                ('reference_code', models.UUIDField(default=uuid.uuid4, null=True)),
                ('account_number', models.CharField(blank=True, max_length=254)),
                ('bank_name', models.CharField(max_length=254)),
                ('bank_code', models.CharField(max_length=254, null=True)),
                ('account_holder', models.CharField(max_length=254, null=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('pre_balance', models.PositiveIntegerField(blank=True, null=True)),
                ('post_balance', models.PositiveIntegerField(blank=True, null=True)),
                ('innovator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.innovator')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.project')),
            ],
        ),
    ]
