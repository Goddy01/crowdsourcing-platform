from django.contrib import messages
from django import forms
from .models import UserProfile, Innovator, Investor, Moderator
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