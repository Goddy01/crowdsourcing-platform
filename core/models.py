from django.db import models, IntegrityError
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
    status = models.CharField(max_length=255, null=True, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    motto = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True, max_length=10000)
    target = models.DecimalField(max_digits=255, decimal_places=2, null=False, blank=False)
    fund_raised = models.DecimalField(max_digits=255, decimal_places=2, null=True, blank=True)
    expected_return = ExpectedReturnField(blank=False, null=False)
    term_months = models.IntegerField(null=False, blank=False)
    country = CountryField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    investment_deadline = models.DateField()
    completed = models.BooleanField(default=False)
    innovator_user_agreement = models.BooleanField(default=False, null=True, blank=True)
    certified_by = models.ForeignKey(account_models.Moderator, on_delete=models.CASCADE, null=True, blank=True)
    # PROJECT GALLERY
    image_1 = models.ImageField(upload_to=upload_project_gallery, blank=False, null=False)
    image_2 = models.ImageField(upload_to=upload_project_gallery, blank=False, null=False)
    image_3 = models.ImageField(upload_to=upload_project_gallery, blank=False, null=False)
    video = models.FileField(upload_to=upload_project_gallery,null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])])    
    business_type = models.CharField(max_length=255)

    def __str__(self):
        return f"Project: {self.name} by {self.innovator.user.username}"
    

class Contribution(models.Model):
    contribution = models.TextField(null=True, blank=True, max_length=10000)
    contributor = models.ForeignKey(account_models.Innovator, on_delete=models.SET_NULL, null=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    accepted = models.BooleanField(default=False)
