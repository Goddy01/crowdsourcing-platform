# Generated by Django 4.2.4 on 2023-09-07 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_remove_innovator_is_project_mgr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='zipcode',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]