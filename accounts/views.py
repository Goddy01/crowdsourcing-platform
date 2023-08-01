from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import InnovatorSignInForm, InnovatorSignUpForm, BaseUserSignUpForm, ModeratorSignUpForm, ModeratorSignInForm, UpdatePersonalProfileForm, UpdateUserResidentialInfoForm, UpdateUserSocialsForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.conf import settings
from django.core.mail import send_mail
from .models import BaseUser, Innovator, Moderator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
from django.forms import ValidationError
from django.core.exceptions import ValidationError
from django.db import transaction


# Create your views here.
def activation_sent_view(request):
    return render(request, 'accounts/activation_sent.html')

def innovator_sign_up(request):
    context = {}
    if request.method == 'POST':
        form = InnovatorSignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                user.is_active = False
                user.date_joined = datetime.now()
                user.last_login = datetime.now()
                user.is_active = True
                # user.signup_confirmation = True
                # user.is_staff = True
                # user.is_verified = True
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
                context['firstname'] = request.POST.get('first_name')
                from_email = settings.EMAIL_HOST_USER
                send_mail(subject, message, from_email, to_email, fail_silently=True)
                return redirect('accounts:activation_sent')
    else:
        form = InnovatorSignUpForm()
    context['innovator_signup_form'] = form
    return render(request, 'accounts/new_sign_up.html', context={'innovator_signup_form': form, 'password1': request.POST.get('password1'), 'password2': request.POST.get('password2')})

def innovator_login(request):
    context = {}
    if request.method == 'POST':
        form = InnovatorSignInForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data.get('email'), password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                if request.POST.get('remember_me') is None:
                    request.session.set_expiry(0)
                    # request.session.modified = True
                else:
                    request.session.set_expiry(1209600)
                user = Innovator.objects.get(user__email=form.cleaned_data.get('email'))
                if user.user.is_verified:
                    return redirect('home')
                return redirect('accounts:edit_profile')
    else:
        form = InnovatorSignInForm()
    context['innovator_signin_form'] = form
    return render(request, 'accounts/new_login.html', {
        'innovator_signin_form': form
    })

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = BaseUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, BaseUser.DoesNotExist):
        user = None
    print('USER_WITHOUT_EMAIL: ', user)
    print('USER_WITH_EMAIL: ', BaseUser.objects.get(email=request.user.email))
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
    if request.user.is_authenticated:
        if request.user.is_admin:
            if request.method == 'POST':
                mod_form = ModeratorSignUpForm(request.POST)
                with transaction.atomic():
                    if mod_form.is_valid():
                        # with transaction.atomic():   
                        # mod_user_obj = baseuser_form.save(commit=False)
                        mod_user_obj = mod_form.save()

                        mod_user_obj.is_active = True
                        mod_user_obj.date_joined = datetime.now()
                        mod_user_obj.last_login = datetime.now()
                        mod_user_obj.signup_confirmation = True
                        mod_user_obj.is_staff = True
                        mod_user_obj.is_verified = True
                        mod_user_obj.save()

                        admin = BaseUser.objects.get(username=request.user.username, is_admin=True)
                        moderator = Moderator.objects.filter(user__email=mod_user_obj.email).update(setup_by_admin=admin)
                        # moderator.setup_by_admin = admin
                        # moderator.save()
                        
                        
                        current_site = get_current_site(request)
                        subject = 'Your Moderator Account Login Details'
                        message = render_to_string('accounts/send_mod_details.html', {
                            'user': admin,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(admin.pk)),
                            'token': account_activation_token.make_token(admin),
                            'to_email': request.POST.get('email'),
                            'password': f"moderator_{request.POST.get('last_name')}",
                        })
                        to_email = [request.POST.get('email')]
                        from_email = settings.EMAIL_HOST_USER
                        send_mail(subject, message, from_email, to_email, fail_silently=True)
                        return redirect('accounts:moderator_account_setup_sent')
            else:
                mod_form = ModeratorSignUpForm()
                # baseuser_form = BaseUserSignUpForm()
                mod_email = request.POST.get('email')
                admin = BaseUser.objects.get(is_admin=True, username=request.user.username)
        else:
            return HttpResponse('Sike! You do not have admin privileges.')
    else:
        return HttpResponse('You must be logged in to access this page')
    return render(request, 'accounts/new_moderator_sign_up.html', {
        # 'mod_base_signup_form': baseuser_form,
        'moderator_signup_form': mod_form,
        'mod_email': request.session.get('mod_email'),
        'admin': request.session.get('admin'),
        'password1': request.POST.get('password1'),
        'password2': request.POST.get('password2')
    })

def moderator_login(request):
    context = {}
    if request.method == 'POST':
        form = ModeratorSignInForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data.get('email'), password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                if request.POST.get('remember_me') is None:
                    request.session.set_expiry(0)
                    # request.session.modified = True
                else:
                    request.session.set_expiry(1209600)
                return redirect('home')
    else:
        form = ModeratorSignInForm()
    context['moderator_login_form'] = form
    return render(request, 'accounts/new_moderator_login.html', context)

@login_required
def sign_out(request):
    logout(request)
    return redirect('home')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('accounts:innovator_login')
    try:
        user = BaseUser.objects.get(username=request.user.username)
    except BaseUser.DoesNotExist:
        return HttpResponse('User Not Found!')
    # else:
    #     user = BaseUser.objects.get(username=request.user.username)
    return render(request, 'accounts/profile.html', {
        'user': user
    })

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('accounts:innovator_login')
    try:
        user = BaseUser.objects.get(username=request.user.username)
    except BaseUser.DoesNotExist:
        return HttpResponse('User Not Found!')
    if request.method == 'POST':
        # email = request.POST.get('email')
        user_p_data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_name': request.POST.get('middle_name'),
            'pfp': request.POST.get('pfp'),
            'phone_num': request.POST.get('phone_num'),
            'date_of_birth': request.POST.get('date_of_birth')
        }
        user_r_data = {
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'country': request.POST.get('country'),
            'address': request.POST.get('address'),
            'zipcode': request.POST.get('zipcode')
        }
        user_p_info = UpdatePersonalProfileForm(user_p_data, request.FILES, instance=request.user)
        user_r_info = UpdateUserResidentialInfoForm(user_r_data, instance=request.user)
        user_s_info = UpdateUserSocialsForm(request.POST, instance=request.user)
        if user_p_info.is_valid() and user_r_info.is_valid() and user_s_info.is_valid():
            user_p_info.save()
            user_r_info.save()
            user_s_info.save()
            return redirect('accounts:profile')
        else:
            print('USER_P_INFO ERRORS: ', user_p_info.errors.as_data())
            print('USER_R_INFO ERRORS: ', user_r_info.errors.as_data())
            print('USER_S_INFO ERRORS: ', user_s_info.errors.as_data())
    else:
        user_p_info = BaseUser.objects.get(username=request.user.username)
        user_p_info = UpdatePersonalProfileForm(instance=request.user, initial= {
            'username': user_p_info.username,
            'email': request.POST.get('email'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_name': request.POST.get('middle_name'),
            'pfp': request.POST.get('pfp'),
            'phone_num': request.POST.get('phone_num'),
            'date_of_birth': request.POST.get('date_of_birth')
        })
        user_r_info = UpdateUserResidentialInfoForm(instance=request.user, initial= {
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'country': request.POST.get('country'),
            'address': request.POST.get('address'),
            'zipcode': request.POST.get('zipcode')
        })
        user_s_info = UpdateUserSocialsForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user,
        'user1': BaseUser.objects.get(username=request.user.username),
        'user_p_info_form': user_p_info,
        'user_r_info_form': user_r_info,
        'user_s_info_form': user_s_info
    })

def resend_email_activation(request):
    context = {}
    user = BaseUser.objects.get(username=request.user.username)
    current_site = get_current_site(request)
    subject = 'Activate your account'
    message = render_to_string('accounts/activation_request.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = [request.user.email]
    context['firstname'] = request.user.first_name
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, to_email, fail_silently=True)
    return redirect('accounts:activation_sent')