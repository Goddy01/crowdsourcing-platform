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
from django.db.models.signals import post_save
import datetime
# Create your models here.


class BaseUserMgr(BaseUserManager):
    """Creates and saves a user with the given details"""
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError("The user must provide an email")
        if not username:
            raise ValueError("The user must provide a username")
        if not first_name:
            raise ValueError("The user must provide an email")
        if not last_name:
            raise ValueError("The user must provide a username")
          # raise ValueError("The user must provide their phone number")
        # try:
        #     UserSocialAuth.objects.get(uid__iexact=email, user=BaseUser.objects.get(email__iexact=email)).social_auth(provider='google-oauth2').extra_data['email']
        # except:
        #     return None
            # return 'This email is linked with an account created through a Google account'

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """Creates and saves a superuser with the given details"""
        user = self.create_user(
            email=email,
            username=username,
            password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        # return user


def upload_location_pfp(instance, filename):
    return f'pfps/{str(instance.username)}/-{filename}'

def upload_location_id_card(instance, filename):
    return f'id_cards/{str(instance.username)}/-{filename}'

class BaseUser(AbstractBaseUser):
    last_name =                     models.CharField(max_length=256, null=True, blank=False)
    first_name =                    models.CharField(max_length=256, null=True, blank=False)
    middle_name =                   models.CharField(max_length=256, null=True, blank=False)
    username =                      models.CharField(max_length=256, unique=True, blank=False)
    date_of_birth =                 models.DateField(null=True, blank=False)
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


    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]

    objects = BaseUserMgr()

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        """Overwrites the base save method"""
        super().save(*args, **kwargs)
        # img = Image.open(self.image.path)
        # if img.height > 300 or img.width > 300:
        #     output_size = (300, 300) # height, width
        #     img.thumbnail(output_size)
        #     img.save(self.image.path)
    
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


# CONTRIBUTOR Model
class Contributor(models.Model):
    user =                          models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    contributions_count =           models.IntegerField(default=0)
    upvotes_received =              models.IntegerField(default=0)
    downvotes_received =            models.IntegerField(default=0)
    reputation_score =              models.IntegerField(default=0)
    is_project_mgr =                models.BooleanField(default=False)
    is_investor =                   models.BooleanField(default=True)
    
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return f"Contributor: {self.user.username}"

    
# MODERATOR Model
class Moderator(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    setup_by_admin = models.OneToOneField(BaseUser, null=True, on_delete=models.CASCADE, related_name='setup_by')
    area_of_expertise = models.CharField(max_length=200)

    def __str__(self):
        return f"Moderator: {self.user.username}"
    
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]


def create_contributor_profile(sender, instance, created, **kwargs):
    if created:
        print('INSTANCE: ', instance.is_active)
        Contributor.objects.create(
            user=instance
            )

post_save.connect(create_contributor_profile, sender=BaseUser)
# post_save.connect(save_contributor_profile, sender=BaseUser)