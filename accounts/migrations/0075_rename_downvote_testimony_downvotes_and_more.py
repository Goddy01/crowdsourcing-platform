# Generated by Django 4.2.4 on 2024-01-11 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0074_rename_dislikes_testimony_downvote_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testimony',
            old_name='downvote',
            new_name='downvotes',
        ),
        migrations.RenameField(
            model_name='testimony',
            old_name='upvote',
            new_name='upvotes',
        ),
    ]
