from django.contrib import messages
from django import forms
from .models import UserProfile, Contributor, Admin, Moderator
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _
from social_django.models import UserSocialAuth


class ContributorSignUpForm(UserCreationForm):
    class Meta:
        model = Contributor
        fields = ['is_project_mgr', 'is_investor']

class ModeratorSignUpForm(UserCreationForm):
    class Meta:
        model = Moderator
        fields = ['area_of_expertise']

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
