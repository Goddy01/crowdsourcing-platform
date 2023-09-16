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
        'required': 'Please enter the expected return of the project'
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
        'required': 'Please check the innovator user agreement box'
    })
    BUSINESS_CHOICES = (
        ("REAL ESTATE", "Real Estate"),
        ("TRANSPORTATION", "Transportation"),
        ("FORESTRY", "Forestry"),
        ("AGRICULTURE", "Agriculture"),
        ("CONSTRUCTION", "Construction"),
        ("ENERGY", "Energy"),
        ("TECHNOLOGY", "Technology"),
        ("HEALTHCARE", "Healthcare"),
        ("CONSUMER GOODS", "Consumer Goods"),
        ("FINANCE AND BANKING", "Finance and Banking"),
        ("HOSPITALITY AND TOURISM", "Hospitality and Tourism"),
        ("ENTERTAINMENT AND MEDIA", "Entertainment and Media"),
        ("MANUFACTURING", "Manufacturing"),
        ("MINING AND NATURAL RESOURCES", "Mining and Natural Resources"),
        ("ENVIRONMENTAL AND SUSTAINABILITY", "Environmental and Sustainability"),
        ("EDUCATION AND EDTECH", "Education and Edtech"),
        )
    business_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=BUSINESS_CHOICES)
    class Meta:
        model = Project
        fields = ['name', 'motto', 'description', 'target', 'expected_return', 'term_months', 'country', 'investment_deadline', 'image_1', 'image_2', 'image_3', 'video', 'business_type', 'innovator_user_agreement']

class CreateInnovationForm(forms.ModelForm):
    class Meta:
        model = ['title', 'description', 'image', 'category', 'reward']