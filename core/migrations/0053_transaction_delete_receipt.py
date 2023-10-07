# Generated by Django 4.2.4 on 2023-10-07 12:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_delete_loadmoney'),
        ('core', '0052_depositmoney'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=254, null=True)),
                ('successful', models.BooleanField(default=False)),
                ('date_generated', models.DateTimeField(auto_now_add=True, null=True)),
                ('reference_code', models.UUIDField(default=uuid.uuid4, null=True)),
                ('amount', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Transaction_owner', to='accounts.innovator')),
            ],
        ),
        migrations.DeleteModel(
            name='Receipt',
        ),
    ]
