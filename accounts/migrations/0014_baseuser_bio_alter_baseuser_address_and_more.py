# Generated by Django 4.2.3 on 2023-07-31 15:56

import accounts.models
from django.db import migrations, models
import django_countries.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_baseuser_country_alter_baseuser_phone_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='bio',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='address',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='city',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='email',
            field=models.EmailField(blank=True, max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='id_card',
            field=models.ImageField(blank=True, null=True, upload_to=accounts.models.upload_location_id_card),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='middle_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='pfp',
            field=models.ImageField(blank=True, null=True, upload_to=accounts.models.upload_location_pfp),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, unique=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='state',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='username',
            field=models.CharField(blank=True, max_length=256, unique=True),
        ),
    ]