from .models import Project, Innovation, Contribution, Transaction, Withdrawal, WithdrawProjectFunds
from accounts.models import KBAQuestion
from django import forms
from ckeditor.fields import RichTextFormField

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
    # STATUS_CHOICES = (
    #     ("ACCEPTED", "Accepted"),
    #     ("DECLINED", "Declined"),
    #     ("REVIEW IN PROGRESS", "Review in Progress"),
    #     ("YET TO BE REVIEWED", "Yet to be reviewed"),
    #     )
    # status = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=STATUS_CHOICES)
    class Meta:
        model = Project
        fields = ['name', 'motto', 'description', 'target', 'expected_return', 'term_months', 'country', 'investment_deadline', 'image_1', 'image_2', 'image_3', 'video', 'business_type', 'innovator_user_agreement']

class CreateInnovationForm(forms.ModelForm):
    title = forms.CharField(error_messages={
        'required': 'Please enter the title of the innovation'
        })
    description = RichTextFormField(error_messages={
        'required': 'Please enter the description about the innovation'
        })
    CATEGORY_CHOICES = (
            ("TECHNOLOGY AND SOFTWARE", "Technology and Software"),
            ("PRODUCT DESIGN", "Product Design"),
            ("HEALTHCARE AND MEDICINE", "Healthcare and Medicine"),
            ("SUSTAINABILITY AND ENVIRONMENT", "Sustainability and Environment"),
            ("EDUCATION AND E-LEARNING", "Education and E-Learning"),
            ("SOCIAL IMPACT", "Social Impact"),
            ("ART AND CREATIVITY", "Art and Creativity"),
            ("BUSINESS AND ENTREPRENEURSHIP", "Business and Entrepreneurship"),
            ("TRAVEL AND TOURISM", "Travel and Tourism"),
            ("ENERGY AND SUSTAINABILITY", "Energy and Sustainability"),
            ("AGRICULTURE AND FOOD", "Agriculture and Food"),
            ("ENTERTAINMENT AND MEDIA", "Entertainment and Media"),
            ("FINANCE AND FINTECH", "Finance and Fintech"),
            ("TRANSPORTATION AND MOBILITY", "Transportation and Mobility"),
            ("SPACE AND AEROSPACE", "Space and Aerospace"),
            ("SPORTS AND FITNESS", "Sports and Fitness"),
            ("SCIENCE AND RESEARCH", "Science and Research"),
            ("FASHION AND APPAREL", "Fashion and Apparel"),
            ("SMART CITIES", "Smart Cities"),
            ("CYBERSECURITY", "Cybersecurity"),
        )
    category = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CATEGORY_CHOICES, error_messages={
        'required': 'Please enter the reward amount'
    })
    reward = forms.IntegerField(error_messages={
        'required': 'Please enter the reward amount'
    })
    class Meta:
        model = Innovation
        fields = ['title', 'description', 'image', 'category', 'reward']

class MakeContributionForm(forms.ModelForm):
    contribution = RichTextFormField(required=False)
    class Meta:
        model = Contribution
        fields = ['contribution']

class MyInvestmentForm(forms.ModelForm):
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
        fields = ['business_type']
class InvestmentStatusForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'),
        ('YET TO BE REVIEWED', 'Yet to be Reviewed'),
        ('REVIEW IN PROGRESS', 'Review In Progress')
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    class Meta:
        model = Project
        fields = ['status']

class StatementTypeForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('INTEREST PAYMENT', 'Interest Payment'),
        ('OUTGOING INVESTMENT', 'Outgoing Investment'),
        ('INCOMING INVESTMENT', 'Incoming Investment'),
        ('OUTGOING TRANSFER', 'Outgoing Transfer'),
        ('INCOMING TRANSFER', 'Incoming Transfer')
    )
    type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TYPE_CHOICES)
    class Meta:
        model = Transaction
        fields = ['type']

class WithdrawalRequestAuthorizationForm(forms.ModelForm):
    TYPE_CHOICES = (
        (False, '-----'),
        (True, 'APPROVED'),
        (False, 'DECLINED'),
        # ('YET TO BE REVIEWED', 'Yet to be Reviewed'),
        # ('REVIEW IN PROGRESS', 'Review In Progress')
    )
    is_approved = forms.ChoiceField(choices=TYPE_CHOICES)
    class Meta:
        model = Withdrawal
        fields = ['is_approved']

class FilterWithdrawalRequestForm(forms.ModelForm):
    TYPE_CHOICES = (
        (True, 'APPROVED'),
        (False, 'DECLINED'),
        # ('YET TO BE REVIEWED', 'Yet to be Reviewed'),
        # ('REVIEW IN PROGRESS', 'Review In Progress')
    )
    is_approved = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TYPE_CHOICES)
    class Meta:
        model = Withdrawal
        fields = ['is_approved']

class FilterConfirmationClickedForm(forms.ModelForm):
    CONFIRM_CHOICES = (
        (True, 'CONFIRMED'),
        (False, 'UNCONFIRMED')
    )
    confirmation_clicked = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CONFIRM_CHOICES)
    class Meta:
        model = Withdrawal
        fields = ['confirmation_clicked']

class KBQForm(forms.ModelForm):
    kbq_answer = forms.CharField(error_messages={
        'required': 'Please enter the answer'
    })
    class Meta:
        model = Withdrawal
        fields = ['kbq_answer']

# class KBQCheckboxForm(forms.ModelForm):
#     class Meta:
#         model = Withdrawal
#         fields = ['kbq_answer']