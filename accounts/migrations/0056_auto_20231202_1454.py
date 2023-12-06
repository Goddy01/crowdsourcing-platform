# Generated by Django 4.2.4 on 2023-12-02 13:54

from django.db import migrations

def set_default_account_balance(apps, schema_editor):
    innovator_model = apps.get_model('accounts', 'Innovator')
    innovator_model.objects.filter(account_balance=None).update(account_balance=0)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0055_alter_innovator_account_balance'),
    ]

    operations = [
        migrations.RunPython(set_default_account_balance),
    ]