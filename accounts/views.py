from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse
from . import forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.conf import settings
from django.core.mail import send_mail
from .models import User, Innovator, Investor, Moderator
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
def activation_sent_view(request):
    return render(request, 'accounts/activation_sent.html')

def innovator_sign_up(request):
    if request.method == 'POST':
        innovator_signup_form = forms.InnovatorSignUpForm(request.POST)
        if innovator_signup_form.is_valid():
            user = innovator_signup_form.save(commit=False)
            user.is_active = False
            user.date_joined = datetime.now()
            user.last_login = datetime.now()
            user.type = "INNOVATOR"
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your account'
            message = render_to_string('accounts/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = [innovator_signup_form.cleaned_data.get('email')]
            from_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, from_email, to_email, fail_silently=True)
            return redirect('accounts:activation_sent')
    else:
        innovator_signup_form = forms.InnovatorSignUpForm()
    return render(request, 'accounts/sign_up.html', context={'innovator_signup_form': innovator_signup_form})

def innovator_sign_in(request):
    if request.method == 'POST':
        innovator_signin_form = forms.InnovatorSignInForm(request.POST)
        if innovator_signin_form.is_valid():
            email = request.POST['email'].lower()
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                # return redirect('home')
                return HttpResponse('Logged In')
    else:
        innovator_signin_form = forms.InnovatorSignInForm()
    return render(request, 'accounts/sign_in.html', context={'innovator_signin_form': innovator_signin_form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Innovator.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Innovator.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.signup_confirmation = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Logged In')
    else:
        return render(request, 'accounts/activation_invalid.html')


@login_required
def sign_out(request):
    logout(request)
    return redirect('home')