from django.contrib import messages
from django import forms
from .models import Contributor, Moderator, BaseUser
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _
from social_django.models import UserSocialAuth
from django.db import transaction


class BaseUserSignUpForm(UserCreationForm):
    class Meta:
        model = BaseUser
        fields = ['last_name', 'first_name', 'username', 'email']
class ContributorSignUpForm(UserCreationForm):
    class Meta:
        model = BaseUser
        fields = ['last_name', 'first_name', 'username', 'email']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        # user.is_teacher = True
        if commit:
            user.save()
        contributor = Contributor.objects.create(user=user)
        return user
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BaseUser.objects.filter(email=email):
            raise forms.ValidationError('A user with this email address already exist.')
        
class ModeratorSignUpForm(UserCreationForm):
    area_of_expertise = forms.CharField(widget=forms.CharField)
    class Meta:
        model = BaseUser
        fields = ['last_name', 'first_name', 'username', 'email', 'area_of_expertise', 'password1', 'password2']

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email'].lower()
            try:
                UserSocialAuth.objects.get(uid__iexact=email, user=BaseUser.objects.get(email__iexact=email)).social_auth(provider='google-oauth2').extra_data['email']
            except:
                raise forms.ValidationError("A Google account is already associated with the email provided.")
class ContributorSignInForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Contributor
        fields = ['email', 'password']

    def clean(self):
        # cleaned_data = super().clean()
        if self.is_valid():
            print('Ani ko lor')
            email = self.cleaned_data['email'].lower()
            password = self.cleaned_data['password']

            user = authenticate(email=email, password=password)

            if user is None:
                try:
                    # Check if the user with the provided email address exists
                    user = Contributor.objects.get(user__email=email)
                except Contributor.DoesNotExist:
                    # Handle the case when the account does not exist
                    raise forms.ValidationError("Account with this email address does not exist.")
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
    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Moderator
        fields = ['email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        if self.is_valid():
            email = self.cleaned_data['email'].lower()
            password = self.cleaned_data['password']

            user = authenticate(email=email, password=password)

            if user is None:
                try:
                    # Check if the user with the provided email address exists
                    user = Moderator.objects.get(email=email)
                except Moderator.DoesNotExist:
                    # Handle the case when the account does not exist
                    raise forms.ValidationError("Account with this email address does not exist.")
                else:
                    # Handle the case when the account exists but login details are invalid
                    raise forms.ValidationError("Invalid login details. Please try again.")

        return cleaned_data
    
    def clean_remember_me(self):
        # Custom validation for the remember_me field if needed
        # For example, you might enforce that it is checked for certain users.
        remember_me = self.cleaned_data.get('remember_me')
        # Your validation logic here
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
