# Generated by Django 4.2.4 on 2024-01-23 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_alter_chat_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
