from __future__ import unicode_literals
from django.db import IntegrityError
from enum import unique
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
# Create your models here.


class AccountManager(BaseUserManager):
    """Creates and saves a user with the given details"""
    def create_user(self, email, username, first_name=None, last_name=None, password=None):
        if not email:
            raise ValueError("The user must provide an email")
        if not username:
            raise ValueError("The user must provide a username")
        
        # Validate email is unique in database
        # if UserProfile.objects.filter(email = self.normalize_email(email).lower()).exists():
        #     raise ValueError('This email has already been registered.')

        # if not middle_name:
        #     raise ValueError("The user must provide their middle_name")
        # if not phone_num:
            # raise ValueError("The user must provide their phone number")

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
    last_name =                     models.CharField(max_length=256)
    first_name =                    models.CharField(max_length=256)
    middle_name =                   models.CharField(max_length=256)
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
        MODERATOR = "MODERATOR", "Moderator"
        INNOVATOR = "INNOVATOR", "Innovator"
        INVESTOR = "INVESTOR", "Investor"

    type =                          models.CharField(max_length=50, default=Types.INNOVATOR, choices=Types.choices, verbose_name='Type')

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