# Generated by Django 4.2.4 on 2023-09-19 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_alter_baseuser_pfp'),
        ('core', '0029_alter_project_approved_by_alter_project_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reward_Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('innovation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='the_innovation', to='core.innovation')),
                ('send_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='accounts.innovator')),
                ('send_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to='accounts.innovator')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='the_user', to='accounts.innovator')),
            ],
        ),
        migrations.CreateModel(
            name='Investment_Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('investment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='the_investment', to='core.innovation')),
                ('send_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_from', to='accounts.innovator')),
                ('send_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_to', to='accounts.innovator')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initiator', to='accounts.innovator')),
            ],
        ),
    ]