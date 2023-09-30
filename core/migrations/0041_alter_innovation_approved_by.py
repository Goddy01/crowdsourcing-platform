# Generated by Django 4.2.4 on 2023-09-20 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_baseuser_is_innovator_baseuser_is_moderator'),
        ('core', '0040_alter_project_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='innovation',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.moderator'),
        ),
    ]