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
