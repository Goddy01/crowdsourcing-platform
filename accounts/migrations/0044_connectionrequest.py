# Generated by Django 4.2.4 on 2023-11-16 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0043_alter_kbaquestion_kba_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_accpeted', models.BooleanField(default=False)),
                ('recipient_has_responded', models.BooleanField(default=False)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connection_recipient', to='accounts.innovator')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connection_requester', to='accounts.innovator')),
            ],
        ),
    ]