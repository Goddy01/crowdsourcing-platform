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
        
        # Validate email is unique in database
        # email = email
        # user = UserProfile.objects.filter(email=email).first()
        # if user:
        # print('EMAIL: ', email)
        # try:
        #     social_auth = UserSocialAuth.objects.get(uid=email, provider='google-oauth2')
        #     if social_auth:
        #         print('1')
        #         return HttpResponse('An email fo google auth dey exieeest')
        # except UserSocialAuth.DoesNotExist:
        #     django_auth = UserProfile.objects.get(email=email)
        #     if django_auth:
        #         print('2')
        #         return HttpResponse('An email fo google auth dey exist')
        # email = email
        # if UserSocialAuth.objects.filter(uid__iexact=email, provider='google-oauth2').exists() or UserProfile.objects.filter(email__iexact=email).exists():
        # if UserProfile.objects.get(email = self.normalize_email(self.social_auth().get('email')).lower()):
            # raise ValidationError('This email has already been registered.')
            # return HttpResponse('This email has already been registered.')

        # if not middle_name:
        #     raise ValueError("The user must provide their middle_name")
        # if not phone_num:
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

class UserProfile(AbstractBaseUser):
    last_name =                     models.CharField(max_length=256, null=False, blank=False)
    first_name =                    models.CharField(max_length=256, null=False, blank=False)
    middle_name =                   models.CharField(max_length=256, null=True, blank=False)
    username =                      models.CharField(max_length=256, unique=True, blank=False)
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
    is_admin =                      models.BooleanField(default=False)
    is_staff =                      models.BooleanField(default=False)
    is_active =                     models.BooleanField(default=True)
    is_superuser =                  models.BooleanField(default=False)
    is_verified =                   models.BooleanField(default=False)
    signup_confirmation =           models.BooleanField(default=False)
    # is_vendor               = models.BooleanField(default=False)
    # is_customer             = models.BooleanField(default=False)


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

class ModeratorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        # When the all() method of this custom manager is called, I will get all users that are moderators.
        return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.MODERATOR)

class InnovatorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        # When the all() method of this custom manager is called, I will get all users that are innovators.
        return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.INNOVATOR)

class InvestorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        # When the all() method of this custom manager is called, I will get all users that are investors.
        return super().get_queryset(*args, **kwargs).filter(type=UserProfile.Types.INVESTOR)

class Moderator(UserProfile):
    objects = ModeratorManager()
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = UserProfile.Types.MODERATOR
        return super().save(*args, **kwargs)

class Innovator(UserProfile):
    objects = InnovatorManager()
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = UserProfile.Types.INNOVATOR
        return super().save(*args, **kwargs)


class Investor(UserProfile):
    objects = InvestorManager()
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = UserProfile.Types.INVESTOR
        return super().save(*args, **kwargs)