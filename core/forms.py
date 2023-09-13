from .models import Project
from django import forms

class CreateProjectForm(forms.ModelForm):
    BUSINESS_CHOICES = (
        ("REAL_ESTATE", "Real Estate"),
        ("TRANSPORTATION", "Transportation"),
        ("FORESTRY", "Forestry"),
        ("AGRICULTURE", "Agriculture"),
        ("CONSTRUCTION", "Construction"),
        ("ENERGY", "Energy"),
        ("TECHNOLOGY", "Technology"),
        ("HEALTHCARE", "Healthcare"),
        ("CONSUMER_GOODS", "Consumer Goods"),
        ("FINANCE_AND_BANKING", "Finance and Banking"),
        ("HOSPITALITY_AND_TOURISM", "Hospitality and Tourism"),
        ("ENTERTAINMENT_AND_MEDIA", "Entertainment and Media"),
        ("MANUFACTURING", "Manufacturing"),
        ("MINING_AND_NATURAL_RESOURCES", "Mining and Natural Resources"),
        ("ENVIRONMENTAL_AND_SUSTAINABILITY", "Environmental and Sustainability"),
        ("EDUCATION_AND_EDTECH", "Education and Edtech"),
        )
    business_type = forms.ChoiceField(widget=forms.RadioSelect, choices=BUSINESS_CHOICES)
    class Meta:
        model = Project
        fields = ['name', 'motto', 'description', 'target', 'expected_return', 'term_months', 'country', 'investment_deadline', 'image_1', 'image_2', 'image_3', 'video', 'business_type', 'innovator_user_agreement']