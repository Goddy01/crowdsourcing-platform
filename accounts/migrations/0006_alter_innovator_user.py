# Generated by Django 4.2.4 on 2023-08-10 10:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_innovator_service_1_alter_innovator_service_2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='innovator',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
