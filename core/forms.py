from .models import Project
from django import forms

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'motto', 'description', 'target', 'expected_return', 'term_months', 'country', 'investment_deadline']