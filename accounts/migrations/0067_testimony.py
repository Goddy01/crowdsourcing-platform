# Generated by Django 4.2.4 on 2024-01-03 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0066_baseuser_receive_msg_email_notif'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimony',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField(max_length=1000)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('testified_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testified_person', to='accounts.innovator')),
                ('testifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testifier', to='accounts.innovator')),
            ],
        ),
    ]
