# Generated by Django 4.2.4 on 2023-12-21 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0065_alter_baseuser_middle_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='receive_msg_email_notif',
            field=models.BooleanField(default=True),
        ),
    ]
