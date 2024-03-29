# Generated by Django 4.2.4 on 2023-11-17 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0048_rename_date_sent_connectionrequest_date_requested'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conn_user1', to='accounts.innovator')),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conn_user2', to='accounts.innovator')),
            ],
        ),
    ]
