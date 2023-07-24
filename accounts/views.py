from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse
from .forms import ContributorSignInForm, ContributorSignUpForm, BaseUserSignUpForm, ModeratorSignUpForm, ModeratorSignInForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.conf import settings
from django.core.mail import send_mail
from .models import BaseUser, Contributor, Moderator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
from django.forms import ValidationError
from django.core.exceptions import ValidationError
from django.db import transaction


# Create your views here.
def activation_sent_view(request):
    return render(request, 'accounts/activation_sent.html')

def contributor_sign_up(request):
    context = {}
    if request.method == 'POST':
        form = ContributorSignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                user.is_active = False
                user.date_joined = datetime.now()
                user.last_login = datetime.now()
                # user.is_project_mgr = form.cleaned_data['is_project_mgr']
                # user.is_project_mgr = form.cleaned_data['is_investor']
                user.save()
                current_site = get_current_site(request)
                subject = 'Activate your account'
                message = render_to_string('accounts/activation_request.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = [form.cleaned_data.get('email')]
                from_email = settings.EMAIL_HOST_USER
                send_mail(subject, message, from_email, to_email, fail_silently=True)
                return redirect('accounts:activation_sent')
        else:
            # for error in form.errors:
            print('ERRORS: ', form.errors.as_data())
    else:
        form = ContributorSignUpForm()
    context['contributor_signup_form'] = form
    return render(request, 'accounts/sign_up.html', context={'contributor_signup_form': form})

def contributor_sign_in(request):
    context = {}
    if request.method == 'POST':
        form = ContributorSignInForm(request.POST)
        # print('ERROR: ', contributor_signin_form)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data.get('email'), password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                return redirect('home')
                    # raise ValueError('This email has already been registered.')
                # return HttpResponse('Logged In')
            else:
                messages.error(request, 'User Not Found')
    else:
        form = ContributorSignInForm()
    context['contributor_signin_form'] = form
    return render(request, 'accounts/sign_in.html', context)

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = BaseUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, BaseUser.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.signup_confirmation = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
        # return HttpResponse('Logged In')
    else:
        return render(request, 'accounts/activation_invalid.html')

def moderation_account_setup_done(request):
    return render(request, 'accounts/moderator_account_setup_sent.html')

def moderator_sign_up(request):
    context = {}
    baseuser_form = BaseUserSignUpForm()  # Define the form here
    mod_form = ModeratorSignUpForm()  # Define the form here
    if request.user.is_authenticated:
        if request.user.is_admin:
            if request.method == 'POST':
                data = {key: value for key, value in request.POST.items() if key != 'area_of_expertise'}
                baseuser_form = BaseUserSignUpForm(data)
                unwanted_mod_form_list = ['first_name', 'last_name', 'username', 'email']
                # data = {key: value for key, value in request.POST.items() if key not in unwanted_mod_form_list}
                mod_form_data = {key: value for key, value in request.POST.items() if key not in unwanted_mod_form_list}
                mod_form = ModeratorSignUpForm(mod_form_data)
                if mod_form.is_valid() and baseuser_form.is_valid():
                    # with transaction.atomic():   
                    base_user_obj = baseuser_form.save(commit=False)
                    mod_user_obj = mod_form.save(commit=False)

                    base_user_obj.is_active = True,
                    base_user_obj.date_joined = datetime.now(),
                    base_user_obj.last_login = datetime.now(),
                    base_user_obj.signup_confirmation = True,
                    base_user_obj.is_staff = True,
                    base_user_obj.is_verified = True
                    
                    mod_user_obj.user = base_user_obj
                    admin = BaseUser.objects.get(username=request.user.username, is_admin=True)
                    mod_user_obj.setup_by_admin = admin
                    
                    base_user_obj.save()
                    mod_user_obj.save()
                    
                    print('ADMIN: ', BaseUser.objects.get(username=request.user.username))
                    
                    current_site = get_current_site(request)
                    subject = 'Your Moderator Account Login Details'
                    message = render_to_string('accounts/send_mod_details.html', {
                        'user': mod_user_obj,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(mod_user_obj.pk)),
                        'token': account_activation_token.make_token(mod_user_obj),
                        'to_email':  base_user_obj.email,
                        'lastname': base_user_obj.last_name,
                        'password': f"moderator_{BaseUser.objects.get(email=request.POST.get('email')).last_name}",
                    })
                else:
                    print('BASE USER FORM ERRORS: ', baseuser_form.errors.as_data())
                    print('MOD USER FORM ERRORS: ', mod_form.errors.as_data())
            else:
                mod_form = ModeratorSignUpForm()
                baseuser_form = BaseUserSignUpForm()
                mod_email = request.POST.get('email')
                admin = BaseUser.objects.get(is_admin=True, username=request.user.username)
        else:
            return HttpResponse('Sike! You do not have admin privileges.')
    else:
        return HttpResponse('You must be logged in to access this page')
    return render(request, 'accounts/moderator_sign_up.html', {
        'mod_base_signup_form': baseuser_form,
        'moderator_signup_form': mod_form,
        'mod_email': request.session.get('mod_email'),
        'admin': request.session.get('admin'),
    })

@login_required
def sign_out(request):
    logout(request)
    return redirect('home')