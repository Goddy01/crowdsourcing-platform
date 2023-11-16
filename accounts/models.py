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
from PIL import Image
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
    job_title =                     models.CharField(max_length=100, null=True, blank=True)
    bio =                           models.CharField(max_length=100, null=True, blank=True)
    about_me =                      models.TextField(null=True, blank=True, max_length=2000)
    pfp =                           models.ImageField(upload_to=upload_location_pfp, blank=True, null=True)
    nin =                           models.CharField(null=True, blank=True, max_length=254)
    # id_card =                       models.ImageField(upload_to=upload_location_id_card, blank=True, null=True)
    city =                          models.CharField(max_length=128, blank=True, null=True)
    state =                         models.CharField(max_length=128, blank=True, null=True)
    country =                       CountryField(max_length=255, null=True, blank=True)
    address =                       models.CharField(max_length=128, blank=True, null=True)
    phone_num =                     PhoneNumberField(null=True, blank=True, verbose_name="Phone Number", unique=True)
    zipcode =                       models.CharField(null=True, blank=True, max_length=255)
    date_joined =                   models.DateTimeField(auto_now_add=True)
    last_login =                    models.DateTimeField(auto_now=True)
    updated_at =                    models.DateTimeField(auto_now=True)
    facebook =                      models.URLField(default='https://facebook.com/')
    twitter =                       models.URLField(default='https://twitter.com/')
    instagram =                     models.URLField(default='https://instagram.com/')
    linkedin =                      models.URLField(default='https://linkedin.com/')
    website =                       models.URLField(default='https://company.com/', null=True, blank=True)
    is_admin =                      models.BooleanField(default=False)
    is_staff =                      models.BooleanField(default=False)
    is_active =                     models.BooleanField(default=True)
    is_superuser =                  models.BooleanField(default=False)
    is_verified =                   models.BooleanField(default=False)
    signup_confirmation =           models.BooleanField(default=False)
    signup_with_google =            models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    is_innovator = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]

    objects = BaseUserMgr()

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        """Overwrites the base save method"""
        super().save(*args, **kwargs)
        if self.pfp:
            img = Image.open(self.pfp.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300) # height, width
                img.thumbnail(output_size)
                img.save(self.pfp.path)
    
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

class KBAQuestion(models.Model):
    KBA_QUESTIONS = [
        ('What is the name of your favorite childhood book?', 'What is the name of your favorite childhood book?'),
        ('In which city were you born?', 'In which city were you born?'),
        ('What is the name of your first pet?', 'What is the name of your first pet?'),
        ('Who was your childhood hero?', 'Who was your childhood hero?'),
        ('What is your favorite childhood movie?', 'What is your favorite childhood movie?'),
        ("What is your mother's maiden name?", "What is your mother's maiden name?"),
        ('What was the name of your first stuffed animal?', 'What was the name of your first stuffed animal?'),
        ('What is the name of your favorite teacher from elementary school?', 'What is the name of your favorite teacher from elementary school?'),
        ('What was your favorite childhood vacation spot?', 'What was your favorite childhood vacation spot?'),
        ('What is the name of your first best friend?', 'What is the name of your first best friend?'),
    ]
    user =                          models.ForeignKey(BaseUser, on_delete=models.CASCADE, null=True, blank=True)
    kba_question =                  models.CharField(max_length=254, blank=True, null=True, choices=KBA_QUESTIONS)
    answer =                        models.CharField(max_length=200, null=True, blank=True)

# CONTRIBUTOR Model
class Innovator(models.Model):
    user =                          models.ForeignKey(BaseUser, on_delete=models.CASCADE, null=True, blank=True)
    innovations_count =             models.IntegerField(default=0, null=True, blank=True)
    upvotes_received =              models.IntegerField(default=0, null=True, blank=True)
    downvotes_received =            models.IntegerField(default=0, null=True, blank=True)
    reputation_score =              models.IntegerField(default=0)   
    is_investor =                   models.BooleanField(default=False)
    account_balance = models.IntegerField(null=True)
    
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        if self.user:
            return self.user.username
        
        return "Innovator"

class InnovatorSkill(models.Model):
    skill_id = models.IntegerField(primary_key=True)
    innovator = models.ForeignKey(Innovator, null=True, on_delete=models.CASCADE)
    skill = models.CharField(max_length=255, null=True, blank=True)
    skill_value = models.IntegerField(null=True, blank=True)

    def __str__(self):
        # if self.innovator.user is not None:
        return f"Innovator-skill_{self.skill_id}"
    
class Service(models.Model):
    user = models.ForeignKey(Innovator, null=True, on_delete=models.CASCADE)
    service = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.user.user.username}-{self.service}"


# MODERATOR Model
class Moderator(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    setup_by_admin = models.ForeignKey(BaseUser, null=True, on_delete=models.CASCADE, related_name='setup_by', unique=False)
    area_of_expertise = models.CharField(max_length=200)

    def __str__(self):
        if not self.user.username:
            return "Moderator"
        
        return f"Moderator: {self.user.username}"
    
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'middle_name', 'phone_num']
    REQUIRED_FIELDS = ['username', ]

class Follow(models.Model):
    follower = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='following')

class ConnectionRequest(models.Model):
    requester = models.ForeignKey(Innovator, on_delete=models.CASCADE, related_name="connection_requester")
    recipient = models.ForeignKey(Innovator, on_delete=models.CASCADE, related_name="connection_recipient")
    is_accepted = models.BooleanField(default=False)
    recipient_has_responded = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.user.username} sent a connection request to {self.recipient.user.username}"