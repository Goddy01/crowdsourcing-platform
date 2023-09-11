from .models import Project
from django import forms

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'motto', 'description', 'target', 'expected_return', 'term_months', 'country', 'investment_deadline', 'image_1', 'image_2', 'image_3', 'video', 'business_type', 'innovator_user_agreement']