from .forms import CustomPasswordResetForm
from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse
from .forms import InnovatorSignInForm, InnovatorSignUpForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.conf import settings
from django.core.mail import send_mail
from .models import UserProfile, Innovator, Investor, Moderator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
from django.core.exceptions import ValidationError

# Create your views here.
def activation_sent_view(request):
    return render(request, 'accounts/activation_sent.html')

def innovator_sign_up(request):
    if request.method == 'POST':
        form = InnovatorSignUpForm(request.POST)
        print('PRINCE')
        if form.is_valid():
            print('GOD IS GOOD')
            user = form.save(commit=False)
            user.is_active = False
            user.date_joined = datetime.now()
            user.last_login = datetime.now()
            user.type = "INNOVATOR"
            user.first_name = user.social_auth.get(provider='linkedin').extra_data['first_name'] or user.social_auth.get(provider='google-oauth2').extra_data['first_name']
            user.last_name = user.social_auth.get(provider='linkedin').extra_data['last_name'] or user.social_auth.get(provider='google-oauth2').extra_data['last_name']
            random_number = random.randint(1000, 9999)  # Generate a random 4-digit number
            user.username = f"{user.social_auth(provider='google-oauth2').extra_data['lastname']}{user.social_auth(provider='google-oauth2').extra_data['firstname']}{random_number}"
            # try:
            user.email = user.social_auth(provider='google-oauth2').extra_data['email']
            # except:
                # except IntegrityError:
                # form.add_error('email', 'This email is already registered.')
            try:
                UserProfile.objects.filter(email=user.social_auth(provider='google-oauth2').extra_data['email']).exists()
                print('BROOOSS')
                return redirect('email-exists')
            except:
                form.add_error('email', 'This email is already registered.')
            #     raise ValueError('This email has already been registered.')
            # try:
            #     UserProfile.objects.get(email=user.social_auth(provider='google-oauth1').extra_data['email']).exists() or UserProfile.objects.get(email=user.email)
            # except ValidationError as e:
            #     return HttpResponse('Email already exists')
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
        form = InnovatorSignUpForm()
    return render(request, 'accounts/sign_up.html', context={'innovator_signup_form': form})

def innovator_sign_in(request):
    context = {}
    print('PRE: ', request.META.get('HTTP_REFERER'))
    if not request.META.get('HTTP_REFERER'):
        context['email_exists'] = 'A Google account is already linked with the email provided.'
    else:
        if request.method == 'POST':
            form = InnovatorSignInForm(request.POST)
            # print('ERROR: ', innovator_signin_form)
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
            form = InnovatorSignInForm()
        context['innovator_signin_form'] = form
    return render(request, 'accounts/sign_in.html', context)

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
        return redirect('home')
        # return HttpResponse('Logged In')
    else:
        return render(request, 'accounts/activation_invalid.html')


@login_required
def sign_out(request):
    logout(request)
    return redirect('home')
    # return HttpResponse('Logged Out')

# def password_reset_view(request):
#     form = CustomPasswordResetForm()
#     print('FORM: ', form)
#     return render(request, 'password/password_reset.html', {'form': form})
def email_exists(request):
    context = {
        'email': 'Email already exists',
    }
    return render(request, 'password/email_exists.html', context)