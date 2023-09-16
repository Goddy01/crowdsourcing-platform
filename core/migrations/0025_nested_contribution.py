# Generated by Django 4.2.4 on 2023-09-16 21:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_rename_innovator_service_user'),
        ('core', '0024_contribution_contributor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nested_Contribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contribution', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('contributor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.innovator')),
                ('parent_contribution', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.contribution')),
            ],
        ),
    ]
