# Generated by Django 4.2.4 on 2023-12-09 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0012_tagchat'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='message_tagged',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply_to', to='chat.chat'),
        ),
        migrations.DeleteModel(
            name='TagChat',
        ),
    ]