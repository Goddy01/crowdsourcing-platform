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
from django.dispatch import receiver
import datetime
from django.contrib.auth.models import PermissionsMixin
from django_countries.fields import CountryField
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

class BaseUser(AbstractBaseUser, PermissionsMixin):
    last_name =                     models.CharField(max_length=256, null=True, blank=True)
    first_name =                    models.CharField(max_length=256, null=True, blank=True)
    middle_name =                   models.CharField(max_length=256, null=True, blank=True)
    username =                      models.CharField(max_length=256, unique=True, blank=True)
    date_of_birth =                 models.DateField(null=True, blank=True)
    email =                         models.EmailField(max_length=128, unique=True, blank=True)
    bio =                           models.CharField(max_length=100, null=True, blank=True)
    pfp =                           models.ImageField(upload_to=upload_location_pfp, blank=True, null=True)
    id_card =                       models.ImageField(upload_to=upload_location_id_card, blank=True, null=True)
    city =                          models.CharField(max_length=128, blank=True, null=True)
    state =                         models.CharField(max_length=128, blank=True, null=True)
    country =                       CountryField(max_length=255, null=True, blank=True)
    address =                       models.CharField(max_length=128, blank=True, null=True)
    phone_num =                     PhoneNumberField(null=True, blank=True, verbose_name="Phone Number", unique=True)
    zipcode =                       models.IntegerField(null=True, blank=True)
    date_joined =                   models.DateTimeField(auto_now_add=True)
    last_login =                    models.DateTimeField(auto_now=True)
    updated_at =                    models.DateTimeField(auto_now=True)
    facebook =                      models.URLField(default='https://facebook.com/')
    twitter =                       models.URLField(default='https://twitter.com/')
    instagram =                     models.URLField(default='https://instagram.com/')
    linkedin =                      models.URLField(default='https://linkedin.com/')
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
class Innovator(models.Model):
    user =                          models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    innovations_count =             models.IntegerField(default=0)
    upvotes_received =              models.IntegerField(default=0)
    downvotes_received =            models.IntegerField(default=0)
    reputation_score =              models.IntegerField(default=0)
    is_project_mgr =                models.BooleanField(default=False)
    is_investor =                   models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return f"Innovator: {self.user.username}"

    
# MODERATOR Model
class Moderator(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    setup_by_admin = models.ForeignKey(BaseUser, null=True, on_delete=models.CASCADE, related_name='setup_by', unique=False)
    area_of_expertise = models.CharField(max_length=200)

    def __str__(self):
        return f"Moderator: {self.user.username}"
    
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]



# @receiver(post_save, sender=Contributor)
# def create_contributor_profile(sender, instance, created, **kwargs):
#     if created:
#         # print('INSTANCE: ', instance.is_staff)
#         # print('THIS', instance.request. META['HTTP_REFERER'])
#         if not instance.is_staff:
#             Contributor.objects.create(
#             user=instance
#             )

# post_save.connect(create_contributor_profile, sender=BaseUser)
# post_save.connect(save_contributor_profile, sender=BaseUser)