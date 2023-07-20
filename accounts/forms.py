from django.contrib import messages
from django import forms
from .models import UserProfile, Contributor, Investor, Reviewer
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _
from social_django.models import UserSocialAuth


class ContributorSignUpForm(UserCreationForm):
    username = forms.CharField(error_messages={'required': 'Please enter your username'})
    first_name = forms.CharField(error_messages={'required': 'Please enter your firstname'})
    last_name = forms.CharField(error_messages={'required': 'Please enter your last name'})
    # middle_name = forms.CharField(error_messages={'required': 'Please enter your middle name'})
    email = forms.CharField(error_messages={'required': 'Please enter your email'})
    password1 = forms.CharField(error_messages={'required': 'Please enter your first password'})
    password2 = forms.CharField(error_messages={'required': 'Please enter your second password'})
    class Meta:
        model = Contributor
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2'] #, 'middle_name'

        # def clean_email(self):
        #     email = self.cleaned_data['email'].lower()
        #     # try:
        #     if UserSocialAuth.objects.filter(uid_iexact=email, provider='google-oauth2').exists():
        #         print('1')
        #         raise forms.ValidationError('An email fo google auth dey exieeest')
        #     # except UserSocialAuth.DoesNotExist:
        #     if UserProfile.objects.filter(email__iexact=email).exists():
        #         print('2')
        #         raise forms.ValidationError('An email fo google auth dey exist')
        #     return email

class ContributorSignInForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'password']

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email'].lower()
            password = self.cleaned_data['password']
            print(email)
            print(password)
            user = authenticate(email=email, password=password)

            print('USER: ', user)
            if not user:
                print('ACCOUNT DOES NOT EXIST')
                raise forms.ValidationError('Invalid login details.')

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
