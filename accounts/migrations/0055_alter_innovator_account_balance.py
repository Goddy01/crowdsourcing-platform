# Generated by Django 4.2.4 on 2023-12-02 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0054_alter_baseuser_pfp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='innovator',
            name='account_balance',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
