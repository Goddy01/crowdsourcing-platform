# Generated by Django 4.2.4 on 2023-09-11 08:51

import core.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0023_alter_baseuser_about_me'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('motto', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, max_length=10000, null=True)),
                ('target', models.DecimalField(decimal_places=2, max_digits=255)),
                ('fund_raised', models.DecimalField(decimal_places=2, max_digits=255)),
                ('expected_return', core.models.ExpectedReturnField(decimal_places=2, max_digits=5)),
                ('term_months', models.IntegerField()),
                ('country', django_countries.fields.CountryField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('investment_deadline', models.DateField()),
                ('completed', models.BooleanField(default=False)),
                ('image_1', models.ImageField(upload_to=core.models.upload_project_gallery)),
                ('image_2', models.ImageField(upload_to=core.models.upload_project_gallery)),
                ('image_3', models.ImageField(upload_to=core.models.upload_project_gallery)),
                ('video', models.FileField(null=True, upload_to=core.models.upload_project_gallery, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])),
                ('business_type', models.CharField(choices=[('REAL ESTATE', 'Real Estate'), ('TRANSPORTATION', 'Transportation'), ('FORESTRY', 'Forestry'), ('AGRICULTURE', 'Agriculture'), ('CONSTRUCTION', 'Construction'), ('ENERGY', 'Enerygy'), ('TECHNOLOGY', 'Technology'), ('HEALTHCARE', 'Healthcare'), ('CONSUMER GOODS', 'Consumer Goods'), ('FINANCE AND BANKING', 'Finance and Banking'), ('HOSPITALITY AND TOURISM', 'Hospitality and Tourism'), ('ENTERTAINMENT AND MEDIA', 'Entertainment and Media'), ('MANUFACTURING', 'Manufacturing'), ('MINING AND NATURAL RESOURCES', 'Mining and Natural Resources'), ('ENVIRONMENTAL AND SUSTAINABILITY', 'Environmental and Sustainability'), ('EDUCATION AND EDTECH', 'Education and Edtech')], max_length=255)),
                ('innovator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.innovator')),
            ],
        ),
    ]
