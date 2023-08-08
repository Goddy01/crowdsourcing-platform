from django.contrib import messages
from django import forms
from .models import Innovator, Moderator, BaseUser, Service
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from social_django.models import UserSocialAuth
from django.db import transaction
from phonenumber_field.formfields import PhoneNumberField
from django_countries.fields import CountryField


class BaseUserSignUpForm(UserCreationForm):
    username = forms.CharField(
            error_messages={
                'required': 'Please enter your username.'
            }
        )
    first_name = forms.CharField(
            error_messages={
                'required': 'Please enter your firstname.'
            }
        )
    last_name = forms.CharField(
            error_messages={
                'required': 'Please enter your lastname.'
            }
        )
    email = forms.EmailField(
            error_messages={
                'required': 'Please enter your email.'
            }
        )
    phone_num = PhoneNumberField(widget=forms.TextInput(), error_messages={
                'required': 'Please enter your phone.'
            }, required=True
        )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput,
            error_messages={
                'required': 'Please enter your password.'
            }
        )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput,
            error_messages={
                'required': 'Please confirm your password by entering it again.'
            }
        )
    class Meta:
        model = BaseUser
        fields = ['last_name', 'first_name', 'username', 'email']

    # def save(self, commit=True):
    #     user = super().save()
    #     # user.is_teacher = True
    #     if commit:
    #         user.save()
    #     # innovator = Innovator.objects.create(user=user)
    #     return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BaseUser.objects.filter(email=email):
            raise forms.ValidationError('A user with this email address already exist.')
        return email
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if BaseUser.objects.filter(username=username):
            raise forms.ValidationError('A user with this username already exist.')
        return username

class InnovatorSignUpForm(UserCreationForm):
    username = forms.CharField(
            error_messages={
                'required': 'Please enter your username.'
            }
        )
    first_name = forms.CharField(
            error_messages={
                'required': 'Please enter your firstname.'
            }
        )
    last_name = forms.CharField(
            error_messages={
                'required': 'Please enter your lastname.'
            }
        )
    email = forms.EmailField(
            error_messages={
                'required': 'Please enter your email.'
            }
        )
    phone_num = PhoneNumberField(widget=forms.TextInput(), error_messages={
                'required': 'Please enter your phone.'
            }, required=True
        )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
            error_messages={
                'required': 'Please enter your password.'
            }
        )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput,
            error_messages={
                'required': 'Please confirm your password by entering it again.'
            }
        )
    
    class Meta:
        model = BaseUser
        fields = ['last_name', 'first_name', 'username', 'email', 'phone_num']

    # @transaction.atomic
    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     # user.is_teacher = True
    #     if commit:
    #         user.save()
    #     innovator = Innovator.objects.create(user=user)
    #     return user
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        # user.is_student = True
        if commit:
            user.save()
        moderator = Innovator.objects.create(user=user)
        return user
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BaseUser.objects.filter(email=email):
            raise forms.ValidationError('A user with this email address already exist.')
        return email
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if BaseUser.objects.filter(username=username):
            raise forms.ValidationError('A user with this username already exist.')
        return username
        
class ModeratorSignUpForm(UserCreationForm):
    username = forms.CharField(
            error_messages={
                'required': 'Please enter your username.'
            }
        )
    first_name = forms.CharField(
            error_messages={
                'required': 'Please enter your firstname.'
            }
        )
    last_name = forms.CharField(
            error_messages={
                'required': 'Please enter your lastname.'
            }
        )
    email = forms.EmailField(
        widget=forms.EmailInput(),
            error_messages={
                'required': 'Please enter your email.'
            }
        )
    phone_num = PhoneNumberField(widget=forms.TextInput(), error_messages={
                'required': 'Please enter your phone.'
            }, required=True
        )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
            error_messages={
                'required': 'Please enter your password.'
            }
        )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput,
            error_messages={
                'required': 'Please confirm your password by entering it again.'
            }
        )
    
    area_of_expertise = forms.CharField(widget=forms.TextInput(),
            error_messages={
                'required': 'Please enter your area of expertise.'
            }
        )
    
    # area_of_expertise = forms.CharField()
    class Meta:
        model = BaseUser
        fields = ['last_name', 'first_name', 'username', 'email', 'area_of_expertise', 'phone_num']
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        # user.is_student = True
        if commit:
            user.save()
        moderator = Moderator.objects.create(user=user, area_of_expertise=self.cleaned_data.get('area_of_expertise'))
        return user
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BaseUser.objects.filter(email=email):
            raise forms.ValidationError('A moderator with this email address already exist.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if BaseUser.objects.filter(username=username):
            raise forms.ValidationError('A moderator with this username already exist.')
        return username

class InnovatorSignInForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(), error_messages={
                'required': 'Please enter your email.'
            })
    password = forms.CharField(widget=forms.PasswordInput(), error_messages={'required': 'Please enter your password'})
    remember_me = forms.BooleanField(required=False, initial=False)
    class Meta:
        model = Innovator
        fields = ['email', 'password']

    def clean(self):
        # cleaned_data = super().clean()
        if self.is_valid():
            email = self.cleaned_data['email'].lower()
            password = self.cleaned_data['password']

            user = authenticate(email=email, password=password)
            # if Innovator.objects.get(user__email=email, signup_confirmation=False):
            #     raise forms.ValidationError("You haven't confirmed your email address")
            if user is not None:
                try:
                    # Check if the user with the provided email address exists
                    user = Innovator.objects.get(user__email=email)
                except:
                    # Handle the case when the account does not exist
                    raise forms.ValidationError("Invalid login details. Please try again.")
            else:
                # Handle the case when the account exists but login details are invalid
                raise forms.ValidationError("Invalid login details. Please try again.")

        # return cleaned_data
    
    def clean_remember_me(self):
        # Custom validation for the remember_me field if needed
        # For example, you might enforce that it is checked for certain users.
        remember_me = self.cleaned_data.get('remember_me')
        # Your validation logic here
        return remember_me

class ModeratorSignInForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(), error_messages={
                'required': 'Please enter your email.'})
    password = forms.CharField(widget=forms.PasswordInput(), error_messages={'required': 'Please enter your password'})
    remember_me = forms.BooleanField(required=False, initial=False)
    class Meta:
        model = Moderator
        fields = ['email', 'password']

    def clean(self):
        # cleaned_data = super().clean()
        if self.is_valid():
            email = self.cleaned_data['email'].lower()
            password = self.cleaned_data['password']

            user = authenticate(email=email, password=password)

            if user is not None:
                try:
                    # Check if the user with the provided email address exists
                    user = Moderator.objects.get(user__email=email)
                except:
                    # Handle the case when the account does not exist
                    raise forms.ValidationError("Invalid login details. Please try again.")
            else:
                # Handle the case when the account exists but login details are invalid
                raise forms.ValidationError("Invalid login details. Please try again.")
    
    def clean_remember_me(self):
        remember_me = self.cleaned_data.get('remember_me')
        return remember_me
    
class CustomPasswordResetForm(PasswordResetForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = forms.CharField(
        label=_("New password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("New password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            print('NIGGA WHAT')
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        print('COOL NIGGA')
        password_validation.validate_password(password2, self.user)
        return password2
class UpdatePersonalProfileForm(forms.ModelForm):
    username = forms.CharField(
                               required=False,
                               widget=forms.TextInput())
    email = forms.EmailField(required=False,
                             widget=forms.TextInput())
    first_name = forms.CharField(
                               required=False,
                               widget=forms.TextInput())
    last_name = forms.CharField(required=False,
                             widget=forms.TextInput())
    middle_name = forms.CharField(
                               required=False,
                               widget=forms.TextInput())
    bio = forms.CharField(
                               required=False,
                               widget=forms.TextInput())
    pfp = forms.ImageField(required=False, widget=forms.FileInput)
    date_of_birth = forms.DateField(required=False)
    phone_num = PhoneNumberField(widget=forms.TextInput(), error_messages={
                'required': 'Please enter your phone.'
            }, required=False
        )
    class Meta:
        model = BaseUser
        fields = ['username', 'email', 'last_name', 'first_name', 'middle_name', 'date_of_birth', 'phone_num', 'bio']

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = BaseUser.objects.exclude(pk=self.instance.pk).get(email=email)
        except BaseUser.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is taken.')

    def clean_phone_num(self):
        phone_num = self.cleaned_data.get('phone_num')
        try:
            user = BaseUser.objects.exclude(pk=self.instance.pk).get(phone_num=phone_num)
        except BaseUser.DoesNotExist:
            return phone_num
        raise forms.ValidationError('This phone number is taken.')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = BaseUser.objects.exclude(pk=self.instance.pk).get(username=username)
        except BaseUser.DoesNotExist:
            return username
        raise forms.ValidationError('This username is taken.')

class UpdateUserResidentialInfoForm(forms.ModelForm):
    city = forms.CharField(
                               required=False,
                               widget=forms.TextInput())
    state = forms.CharField(required=False,
                             widget=forms.TextInput())
    country = CountryField(blank=True)
    address = forms.CharField(required=False,
                             widget=forms.TextInput())
    zipcode = forms.IntegerField(required=False)
    class Meta:
        model = BaseUser
        fields = ['city', 'state', 'country', 'address', 'zipcode']

class UpdateUserSkills(forms.ModelForm):
    class Meta:
        model = BaseUser
        fields  = ['skill_1', 'skill_2', 'skill_3', 'skill_4', 'skill_5', 'skill_6', 'skill_7', 'skill_8', 'skill_9', 'skill_10']


class UpdateUserSocialsForm(forms.ModelForm):
    facebook = forms.URLField(required=False)
    twitter = forms.URLField(required=False)
    instagram = forms.URLField(required=False)
    linkedin = forms.URLField(required=False)
    website = forms.URLField(required=False)
    class Meta:
        model = BaseUser
        fields = ['facebook', 'twitter', 'instagram', 'linkedin', 'website']

class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = BaseUser
        fields = ['new_password1', 'new_password2']

class UpdateUserServicesForm(forms.Form)        :
    service_1 = forms.CharField(required=False)
    service_2 = forms.CharField(required=False)
    service_3 = forms.CharField(required=False)
    service_4 = forms.CharField(required=False)
    service_5 = forms.CharField(required=False)
    class Meta:
        model = Innovator
        fields = ('service_1', 'service_2', 'service_3', 'service_4', 'service_5')