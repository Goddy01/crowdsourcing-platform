# Generated by Django 4.2.4 on 2023-10-07 09:16

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_delete_loadmoney'),
        ('core', '0051_alter_project_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepositMoney',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0, null=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('reference_code', models.UUIDField(default=uuid.uuid4, null=True)),
                ('innovator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.innovator')),
            ],
        ),
    ]
