import json, re
from collections.abc import Iterable
from django.contrib.postgres.fields import ArrayField
import uuid
from django.db import models, IntegrityError
from accounts import models as account_models
from django_countries.fields import CountryField
from PIL import Image
from django.core.validators import FileExtensionValidator
from ckeditor.fields import RichTextField
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
    return f'project_gallery/{instance.innovator.user.last_name}-{instance.innovator.user.first_name}-{instance.innovator.user.middle_name}/project-{instance.name}/-{filename}'


def upload_innovation_images(instance, filename):
    return f'innovation_images/{instance.owner.user.last_name}-{instance.owner.user.first_name}-{instance.owner.user.middle_name}/innovation-{instance.title}/-{filename}'

def upload_project_milestone_gallery(instance, filename):
    return f'project_milestone_gallery/{instance.project.innovator.user.last_name}-{instance.project.innovator.user.first_name}-{instance.project.innovator.user.middle_name}/project-{instance.title}/-{filename}'

# PROJECT
class Project(models.Model):
    innovator = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, null=True, blank=True, default='YET TO BE REVIEWED')
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    motto = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True, max_length=10000)
    target = models.DecimalField(max_digits=255, decimal_places=2, null=False, blank=False)
    fund_raised = models.DecimalField(max_digits=255, decimal_places=2, null=True, blank=True, )
    amount_left = models.DecimalField(max_digits=255, decimal_places=2, null=True, blank=True, )
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
    business_type = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(account_models.Moderator, on_delete=models.SET_NULL, null=True, related_name='approved_name', blank=True)

    @property
    def fund_raised_percentage(self):
        if self.fund_raised is None:
            self.fund_raised = 0
        if self.target > 0:
            return (self.fund_raised / self.target) * 100
        else:
            return 0  # To handle the case where target is 0 (to avoid division by zero)

    @property
    def count_make_investments_instances(self):
        return self.the_investment.count()
    
    def total_investment_capital_balance(self):
        amount = 0
        for project in Project.objects.filter(innovator=self.innovator):
            amount += project.fund_raised
        return amount
    
    def get_business_categories_list(self):
        """Return a list of individual business categories."""
        # content_inside_brackets = self.business_type[self.business_type.find('[') + 1:self.business_type.rfind(']')]

        # # Split the content into a list based on commas
        # category_list = [category.strip(" '") for category in content_inside_brackets.split(',')]

        # # Print the result
        # return category_list

        matches = re.search(r'\[([^\]]+)\]', self.business_type)

        # Check if there are matches and extract the content
        if matches:
            content_inside_brackets = matches.group(1)
            # Split the content into a list based on commas
            category_list = [category.strip(" '") for category in content_inside_brackets.split(',')]
            # Print the result
            return category_list
        else:
            return None

    def set_business_categories_list(self, categories):
        """Set business categories based on a list."""
        self.business_type = ','.join(categories)
        
    def __str__(self):
        return f"Project: {self.name} by {self.innovator.user.username}"
    

class Innovation(models.Model):
    title = models.CharField(max_length=255, null=True, blank=False)
    description = RichTextField(null=True, blank=False)
    owner = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=upload_innovation_images, blank=True, null=True)
    status = models.CharField(default='Unapproved', max_length=255)
    category = models.CharField(max_length=255, null=True, blank=False)
    upvotes = models.IntegerField()
    downvotes = models.IntegerField()
    num_of_contributions = models.IntegerField(blank=True, null=True)
    reward = models.DecimalField(max_digits=255, decimal_places=2, null=False, blank=False)
    reward_paid = models.BooleanField(default=False)
    views = models.IntegerField()
    approved_by = models.ForeignKey(account_models.Moderator, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Innovation: {self.title} by {self.owner.user.username}"
    
    class Meta:
        unique_together = ('title', 'owner')

class Contribution(models.Model):
    contribution = RichTextField(null=True, blank=True)
    contributor = models.ForeignKey(account_models.Innovator, on_delete=models.SET_NULL, null=True)
    innovation = models.ForeignKey(Innovation, on_delete=models.SET_NULL, null=True)
    parent=models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name='parent_contrib')
    upvotes = models.IntegerField(null=True, blank=True, default=0)
    downvotes = models.IntegerField(null=True, blank=True, default=0)
    upvoted_by = models.ManyToManyField(account_models.Innovator, related_name='upvoted_contributions', blank=True)
    downvoted_by = models.ManyToManyField(account_models.Innovator, related_name='downvoted_contributions', blank=True)
    accepted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        if self.contributor is not None:
            return f"Contribution by {self.contributor.user.username}"
        else:
            return "a"
        
class Reward_Payment(models.Model):
    send_to = models.ForeignKey(account_models.Innovator, null=False, blank=False, on_delete=models.CASCADE, related_name='recipient')
    send_from = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, blank=False, null=False, related_name='sender')
    user = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, null=False, blank=False, related_name='the_user')
    amount = models.IntegerField()
    innovation = models.ForeignKey(Innovation, on_delete=models.CASCADE, null=False, blank=False, related_name='the_innovation')
    date_sent = models.DateTimeField(auto_now_add=True, null=True)


class Make_Investment(models.Model):
    send_to = models.ForeignKey(account_models.Innovator, null=False, blank=False, on_delete=models.CASCADE, related_name='receiver')
    send_from = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, blank=False, null=False, related_name='send_from')
    sender = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, null=False, blank=False, related_name='investor')
    amount = models.IntegerField()
    investment = models.ForeignKey(Project, on_delete=models.CASCADE, null=False, blank=False, related_name='the_investment')
    expected_return = models.DecimalField(max_digits=255, decimal_places=2, blank=False, null=True)
    date_sent = models.DateTimeField(auto_now_add=True, null=True)
    reference_code = models.UUIDField(default=uuid.uuid4, null=True)


class Transaction(models.Model):
    owner = models.ForeignKey(account_models.Innovator, null=False, blank=False, on_delete=models.CASCADE, related_name='Transaction_owner')
    description = models.CharField(null=True, blank=True, max_length=254)
    successful = models.BooleanField(default=False)
    date_generated = models.DateTimeField(auto_now_add=True, null=True)
    reference_code = models.UUIDField(default=uuid.uuid4, null=True)
    amount = models.PositiveIntegerField(null=True, blank=True)
    pre_balance = models.PositiveIntegerField(null=True, blank=True)
    post_balance = models.PositiveIntegerField(null=True, blank=True)
    type = models.CharField(null=True, blank=True, max_length=254)
    def __str__(self):
        if self.owner.user.middle_name:
            return F"Transaction by {self.owner.user.last_name}, {self.owner.user.first_name} {self.owner.user.middle_name}"
        else:
            return F"Transaction by {self.owner.user.first_name} {self.owner.user.last_name}"
        
class DepositMoney(models.Model):
    amount = models.IntegerField(null=True, blank=False, default=0)
    innovator = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, null=True, blank=False)
    date = models.DateTimeField(auto_now_add=True, null=True)
    reference_code = models.UUIDField(default=uuid.uuid4, null=True)
    pre_balance = models.PositiveIntegerField(null=True, blank=True)
    post_balance = models.PositiveIntegerField(null=True, blank=True)

class Withdrawal(models.Model):
    amount = models.PositiveIntegerField(null=True, blank=True)
    reference_code = models.UUIDField(default=uuid.uuid4, null=True)
    account_number = models.CharField(null=False, blank=True, max_length=254)
    bank_name = models.CharField(max_length=254, null=False, blank=False)
    bank_code = models.CharField(max_length=254, null=True, blank=False)
    account_holder = models.CharField(max_length=254, null=True, blank=False)
    innovator = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True, null=True)
    pre_balance = models.PositiveIntegerField(null=True, blank=True)
    post_balance = models.PositiveIntegerField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    confirmation = models.BooleanField(default=False, null=True, blank=True)
    confirmation_clicked = models.BooleanField(default=False, null=True, blank=True)
    kbq_answer = models.CharField(max_length=254, null=True, blank=True)
    kbq_answer_status = models.CharField(max_length=254, null=True, blank=True)
    approved_by = models.ForeignKey(account_models.Moderator, on_delete=models.CASCADE, null=True, blank=True)
    withdrawal_status  = models.CharField(max_length=254, null=True, blank=True)
    date_approved = models.DateTimeField(auto_now=True, null=True)
    # post_withdrawal_account_balance = models.PositiveBigIntegerField(null=False, blank=False)

    @property
    def post_withdrawal_account_balance(self):
        balance = self.innovator.account_balance - self.amount
        return balance

class WithdrawProjectFunds(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=True)
    reference_code = models.UUIDField(default=uuid.uuid4, null=True)
    account_number = models.CharField(null=False, blank=True, max_length=254)
    bank_name = models.CharField(max_length=254, null=False, blank=False)
    bank_code = models.CharField(max_length=254, null=True, blank=False)
    account_holder = models.CharField(max_length=254, null=True, blank=False)
    innovator = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True, null=True)
    pre_balance = models.PositiveIntegerField(null=True, blank=True)
    post_balance = models.PositiveIntegerField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    confirmation = models.BooleanField(default=False, null=True, blank=True)
    confirmation_clicked = models.BooleanField(default=False, null=True, blank=True)
    kbq_answer = models.CharField(max_length=254, null=True, blank=True)
    kbq_answer_status = models.CharField(max_length=254, null=True, blank=True)
    approved_by = models.ForeignKey(account_models.Moderator, on_delete=models.CASCADE, null=True, blank=True)
    withdrawal_status  = models.CharField(max_length=254, null=True, blank=True)
    date_approved = models.DateTimeField(auto_now=True, null=True)
    
class SendMoney(models.Model):
    amount = models.PositiveIntegerField(null=True, blank=True)
    reference_code = models.UUIDField(default=uuid.uuid4, null=True)
    sender = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, null=False, blank=False, related_name='money_sender')
    recipient = models.ForeignKey(account_models.Innovator, on_delete=models.CASCADE, null=False, related_name='money_recipient')
    date = models.DateTimeField(auto_now_add=True, null=True)
    pre_balance = models.PositiveIntegerField(null=True, blank=True)
    post_balance = models.PositiveIntegerField(null=True, blank=True)
    is_approved = models.BooleanField(default=False, null=True, blank=True)

    
    def create_receive_money_instance(self):
        recipient_pre_balance = self.recipient.account_balance - self.amount
        transaction = Transaction.objects.create(
            owner=self.recipient,
            description = f"You received ₦{self.amount} from {self.sender.user.username}",
            successful = not False,
            reference_code = self.reference_code,
            amount = self.amount,
            pre_balance = recipient_pre_balance,
            post_balance = recipient_pre_balance + self.amount,
            type = 'INCOMING TRANSFER'
        )
        return transaction


    def __str__(self) -> str:
        return f"{self.sender.user.username} sent ₦{self.amount} to {self.recipient.user.username}"
    
class ProjectMilestone(models.Model):
    MILESTONE_STATUS = (
        ('DELAYED', 'Delayed'),
        ('IN PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),

    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    description = models.TextField(null=True, blank=True, max_length=10000)
    target_date = models.DateField()
    progress_report = RichTextField(null=True, blank=True)
    # PROJECT MILESTONE GALLERY
    image_1 = models.ImageField(upload_to=upload_project_milestone_gallery, blank=True, null=True, max_length=254)
    image_2 = models.ImageField(upload_to=upload_project_milestone_gallery, blank=True, null=True, max_length=254)
    image_3 = models.ImageField(upload_to=upload_project_milestone_gallery, blank=True, null=True, max_length=254)
    video = models.FileField(upload_to=upload_project_milestone_gallery, null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])], max_length=254)    
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    status = models.CharField(max_length=254, blank=False, null=True, choices=MILESTONE_STATUS)