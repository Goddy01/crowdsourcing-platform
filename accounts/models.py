from django.http import HttpResponse, HttpResponseRedirect
from django.db import IntegrityError
from enum import unique
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.core.exceptions import ValidationError
from social_django.models import UserSocialAuth
from django.shortcuts import redirect
# Create your models here.


class AccountManager(BaseUserManager):
    """Creates and saves a user with the given details"""
    def create_user(self, email, username, first_name=None, last_name=None, password=None):
        if not email:
            raise ValueError("The user must provide an email")
        if not username:
            raise ValueError("The user must provide a username")
          # raise ValueError("The user must provide their phone number")
        try:
            UserSocialAuth.objects.get(uid__iexact=email, user=UserProfile.objects.get(email__iexact=email)).social_auth(provider='google-oauth2').extra_data['email']
        except:
            print('111BROOOSS')
            return None
            # return 'This email is linked with an account created through a Google account'

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            # middle_name=middle_name,
            # phone_num=phone_num
        )
        user.set_password(password)
        # Save and catch IntegrityError (due to email being unique)
        # try:
        user.save(using=self._db)
        # except IntegrityError:
        #     raise ValueError('This email has already been registered.')
        # return user

    def create_superuser(self, email, username, first_name, last_name, password):
        """Creates and saves a superuser with the given details"""
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            # middle_name=middle_name,
            # phone_num=phone_num,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)


def upload_location_pfp(instance, filename):
    return f'pfps/{str(instance.username)}/-{filename}'

def upload_location_id_card(instance, filename):
    return f'id_cards/{str(instance.username)}/-{filename}'

class BaseUser(AbstractBaseUser):
    last_name =                     models.CharField(max_length=256, null=False, blank=False)
    first_name =                    models.CharField(max_length=256, null=False, blank=False)
    middle_name =                   models.CharField(max_length=256, null=True, blank=False)
    username =                      models.CharField(max_length=256, unique=True, blank=False)
    date_of_birth =                 models.DateField()
    email =                         models.EmailField(max_length=128, unique=True, blank=False)
    pfp =                           models.ImageField(upload_to=upload_location_pfp, blank=False, null=True)
    id_card =                       models.ImageField(upload_to=upload_location_id_card, blank=False, null=True)
    city =                          models.CharField(max_length=128, blank=False, null=True)
    state =                         models.CharField(max_length=128, blank=False, null=True)
    country =                       models.CharField(max_length=128, blank=False, null=True)
    address =                       models.CharField(max_length=128, blank=False, null=True)
    phone_num =                     PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")
    date_joined =                   models.DateTimeField(auto_now_add=True)
    last_login =                    models.DateTimeField(auto_now=True)
    updated_at =                    models.DateTimeField(auto_now=True)
    facebook =                      models.URLField(default='https://facebook.com/')
    twitter =                       models.URLField(default='https://twitter.com/')
    instagram =                     models.URLField(default='https://instagram.com/')
    is_admin =                      models.BooleanField(default=False)
    is_staff =                      models.BooleanField(default=False)
    is_active =                     models.BooleanField(default=True)
    is_superuser =                  models.BooleanField(default=False)
    is_verified =                   models.BooleanField(default=False)
    signup_confirmation =           models.BooleanField(default=False)
    is_projectmgr                 = models.BooleanField(default=False)
    is_moderator                  = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]

    objects = AccountManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        '''Returns the first_name plus the last_name, with a space in between.'''
        full_name = '%s, %s %s' % (self.last_name, self.first_name, self.middle_name)
        return full_name.strip()

    def has_perm(self, perm, obj=None):
        """Checks if the user has any permissions"""
        return self.is_admin

    def has_module_perms(self, app_label):
        """Checks if the user has permission to view the app 'app_label'"""
        return True

    class Types(models.TextChoices):
        CONTRIBUTOR = "CONTRIBUTOR", "Contributor"
        REVIEWER = "REVIEWER", "Reviewer"
        INVESTOR = "INVESTOR", "Investor"
        PROJECT_MANAGER = "PROJECT MANAGER", "Project Manager"
        ADMINISTRATOR = "ADMINISTRATOR", "Administrator"

    type =                          models.CharField(max_length=50, default=Types.CONTRIBUTOR, choices=Types.choices, verbose_name='Type')

# CONTRIBUTOR Model
class Contributor(models.Model):
    user =                          models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    contributions_count =           models.IntegerField(default=0)
    upvotes_received =              models.IntegerField(default=0)
    downvotes_received =            models.IntegerField(default=0)
    reputation_score =              models.IntegerField(default=0)

    def __str__(self):
        return f"Contributor: {self.user.email}"
    
class Moderator(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    area_of_expertise = models.CharField(max_length=200)

    def __str__(self):
        return f"Moderator: {self.user.email}"

class ReviewerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        # When the all() method of this custom manager is called, I will get all users that are moderators.
        return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.REVIEWER)

class ContributorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        # When the all() method of this custom manager is called, I will get all users that are innovators.
        return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.CONTRIBUTOR)

class InvestorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        # When the all() method of this custom manager is called, I will get all users that are investors.
        return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.INVESTOR)
# class Project_MngrManager(models.Manager):
#     def get_queryset(self, *args, **kwargs):
#         # When the all() method of this custom manager is called, I will get all users that are innovators.
#         return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.PROJECT_MANAGER)

class AdministratorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        # When the all() method of this custom manager is called, I will get all users that are investors.
        return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.ADMINISTRATOR)

class Reviewer(UserProfile):
    objects = ReviewerManager()
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = UserProfile.Types.REVIEWER
        return super().save(*args, **kwargs)

class Contributor(UserProfile):
    objects = ContributorManager()
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = UserProfile.Types.CONTRIBUTOR
        return super().save(*args, **kwargs)

class Investor(UserProfile):
    objects = InvestorManager()
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = UserProfile.Types.INVESTOR
        return super().save(*args, **kwargs)

# class Project_Manager(UserProfile):
#     objects = Project_MngrManager()
#     class Meta:
#         proxy = True

#     def save(self, *args, **kwargs):
#         if not self.pk:
#             self.type = UserProfile.Types.PROJECT_MANAGER
#         return super().save(*args, **kwargs)

class Administrator(UserProfile):
    objects = AdministratorManager()
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = UserProfile.Types.ADMINISTRATOR
        return super().save(*args, **kwargs)