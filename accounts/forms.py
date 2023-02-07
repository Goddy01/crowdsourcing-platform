from django import forms
from .models import User, Innovator, Investor, Moderator
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

class InnovatorSignUpForm(UserCreationForm):
    username = forms.CharField(error_messages={'required': 'Please enter your username'})
    first_name = forms.CharField(error_messages={'required': 'Please enter your firstname'})
    last_name = forms.CharField(error_messages={'required': 'Please enter your last name'})
    middle_name = forms.CharField(error_messages={'required': 'Please enter your middle name'})
    email = forms.CharField(error_messages={'required': 'Please enter your email'})
    password1 = forms.CharField(error_messages={'required': 'Please enter your first password'})
    password2 = forms.CharField(error_messages={'required': 'Please enter your second password'})
    class Meta:
        model = Innovator
        fields = ['username', 'first_name', 'last_name', 'middle_name', 'email', 'password1', 'password2']

class InnovatorSignInForm(forms.ModelForm):
    class Meta:
        model = Innovator
        fields = ['email', 'password']

    def clean(self):
        email = self.cleaned_data.get('email').lower()
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)

        if user is None:
            raise forms.ValidationError('Account does not exist.')