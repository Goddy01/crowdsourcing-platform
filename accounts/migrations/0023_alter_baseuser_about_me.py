# Generated by Django 4.2.4 on 2023-09-09 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_remove_innovator_about_me_baseuser_about_me'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='about_me',
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
    ]