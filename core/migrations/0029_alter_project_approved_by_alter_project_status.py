# Generated by Django 4.2.4 on 2023-09-18 06:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_follow'),
        ('core', '0028_contribution_downvoted_by_contribution_upvoted_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_name', to='accounts.moderator'),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
