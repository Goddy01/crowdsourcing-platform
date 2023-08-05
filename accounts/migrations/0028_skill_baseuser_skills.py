# Generated by Django 4.2.3 on 2023-08-05 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_alter_baseuser_pfp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='baseuser',
            name='skills',
            field=models.ManyToManyField(blank=True, null=True, to='accounts.skill'),
        ),
    ]
