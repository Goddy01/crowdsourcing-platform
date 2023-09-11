from django.db import models
from accounts import models as account_models
from django_countries.fields import CountryField
from PIL import Image
from django.core.validators import FileExtensionValidator
# Create your models here.

# EXPECTED RETURN
class ExpectedReturnField(models.DecimalField):
    """
    A custom DecimalField to represent the expected return for an investment or project.
    """
    max_digits = 5  # Adjust this based on your specific needs
    decimal_places = 2  # Adjust this based on your specific needs

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = self.max_digits
        kwargs['decimal_places'] = self.decimal_places
        super().__init__(*args, **kwargs)


def upload_project_gallery(instance, filename):
    return f'project_gallery/{instance.innovator.user.last_name} {instance.innovator.user.first_name} {instance.innovator.user.middle_name}/project-{instance.name}/-{filename}'


# PROJECT
class Project(models.Model):
    innovator = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)
    motto = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True, max_length=10000)
    target = models.DecimalField(max_length=255, decimal_places=2, null=False, blank=False)
    fund_raised = models.DecimalField(max_length=255, decimal_places=2, null=False, blank=False)
    expected_return = ExpectedReturnField(blank=False, null=False)
    term_months = models.IntegerField(null=False, blank=False)
    country = CountryField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    investment_deadline = models.DateField()
    completed = models.BooleanField(default=False)
    
    # PROJECT GALLERY
    image_1 = models.ImageField(upload_to=upload_project_gallery, blank=False, null=False)
    image_2 = models.ImageField(upload_to=upload_project_gallery, blank=False, null=False)
    image_3 = models.ImageField(upload_to=upload_project_gallery, blank=False, null=False)
    video = models.FileField(upload_to=upload_project_gallery,null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])])
    
    
    class Investment_type(models.TextChoices):
        REAL_ESTATE = "REAL ESTATE", "Real Estate"
        TRANSPORTATION = "TRANSPORTATION", "Transportation"
        FORESTRY = "FORESTRY", "Forestry"
        AGRICULTURE = "AGRICULTURE", "Agriculture"
        CONSTRUCTION = "CONSTRUCTION", "Construction"
        ENERGY = "ENERGY", "Enerygy"
        TECHNOLOGY = "TECHNOLOGY", "Technology"
        HEALTHCARE = "HEALTHCARE", "Healthcare"
        CONSUMER_GOODS = "CONSUMER GOODS", "Consumer Goods"
        FINANCE_AND_BANKING = "FINANCE AND BANKING", "Finance and Banking"
        HOSPITALITY_AND_TOURISM = "HOSPITALITY AND TOURISM", "Hospitality and Tourism"
        ENTERTAINMENT_AND_MEDIA = "ENTERTAINMENT AND MEDIA", "Entertainment and Media"
        MANUFACTURING = "MANUFACTURING", "Manufacturing"
        MINING_AND_NATURAL_RESOURCES = "MINING AND NATURAL RESOURCES", "Mining and Natural Resources"
        ENVIRONMENTAL_AND_SUSTAINABILITY = "ENVIRONMENTAL AND SUSTAINABILITY", "Environmental and Sustainability"
        EDUCATION_AND_EDTECH = "EDUCATION AND EDTECH", "Education and Edtech"
    
    business_type = models.CharField(max_length=255, choices=Investment_type.choices)