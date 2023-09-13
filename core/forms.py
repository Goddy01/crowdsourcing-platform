from .models import Project
from django import forms

class CreateProjectForm(forms.ModelForm):
    name = forms.CharField(error_messages={
        'required': 'Please enter the name of the project'
    })
    motto = forms.CharField(error_messages={
        'required': 'Please enter the aim of the project'
    })
    description = forms.CharField(error_messages={
        'required': 'Please enter the description of the project'
    })
    target = forms.IntegerField(error_messages={
        'required': 'Please enter the target amount of the project'
    })
    expected_return = forms.DecimalField(error_messages={
        'required': 'Please enter the expected_return of the project'
    })
    term_months = forms.IntegerField(error_messages={
        'required': 'Please enter the term of the project in months'
    })
    country = forms.CharField(error_messages={
        'required': 'Please enter the country where the project is located.'
    })
    investment_deadline = forms.DateField(error_messages={
        'required': 'Please enter the investment deadline of the project'
    })
    image_1 = forms.ImageField(error_messages={
        'required': 'Please attach the first image about the project'
    })
    image_2 = forms.ImageField(error_messages={
        'required': 'Please attach the second image about the project'
    })
    image_3 = forms.ImageField(error_messages={
        'required': 'Please attach the third image about the project'
    })
    video = forms.FileField(error_messages={
        'required': 'Please attach a video explaining the project details'
    })
    business_type = forms.ChoiceField(error_messages={
        'required': 'Please select a category where the project belongs'
    })
    innovator_user_agreement = forms.BooleanField(error_messages={
        'required': 'Please check the box'
    })
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