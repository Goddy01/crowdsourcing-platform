from django.db.models import Q
from datetime import datetime
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import InnovatorSignInForm, InnovatorSignUpForm, BaseUserSignUpForm, ModeratorSignUpForm, ModeratorSignInForm, UpdatePersonalProfileForm, UpdateUserResidentialInfoForm, UpdateUserSocialsForm, ChangePasswordForm, UpdateUserSkillsForm, UpdateInnovatorServicesForm, UpdateUserServiceForm, UpdateUserNINForm, UpdateKBAQuestionForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.conf import settings
from django.core.mail import send_mail
from .models import BaseUser, Innovator, Moderator, Follow, KBAQuestion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
from django.forms import ValidationError, modelformset_factory
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.forms import formset_factory
from django.forms.models import modelformset_factory
from .models import InnovatorSkill, Service, ConnectionRequest, Connection
from django import forms
from django.contrib import messages
from core.models import Project
from django.http import HttpResponseRedirect
from core.models import Make_Investment
import requests


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
                # user.username = user.username.lower()
                # user.signup_confirmation = True
                # user.is_staff = True
                # user.is_verified = True
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
        'user': user,
        'user_skills': InnovatorSkill.objects.filter(innovator__user__pk=request.user.pk),
        'user_services': Service.objects.filter(user__pk=request.user.pk)
        
    })


def mod_profile(request):
    if not request.user.is_authenticated:
        return redirect('accounts:moderator_login')
    try:
        user = BaseUser.objects.get(username=request.user.username)
    except BaseUser.DoesNotExist:
        return HttpResponse('User Not Found!')
    # else:
    #     user = BaseUser.objects.get(username=request.user.username)
    return render(request, 'accounts/mod_profile.html', {
        'user': user,
        # 'user_skills': Innovator.objects.get(user__username=request.user.username).innovatorskill_set.all(),
        'user_services': Service.objects.filter(user=request.user.pk)
        
    })

def others_profile(request, innovator_pk):
    innovator = Innovator.objects.get(pk=innovator_pk)
    innovator_skills = InnovatorSkill.objects.filter(innovator__pk=innovator_pk)
    innovator_services = Service.objects.filter(user__pk=innovator_pk)
    projects = Project.objects.filter(innovator=innovator)[:3]
    conn_request = ConnectionRequest.objects.filter(
        requester=Innovator.objects.get(user__pk=request.user.pk),
        recipient=innovator,
    )
    
    user1 = innovator
    user2 = Innovator.objects.get(user__pk=request.user.pk)
    friends = Connection.objects.filter(
        (Q(user1=user1) & Q(user2=user2)) |
        (Q(user1=user2) & Q(user2=user1))
    ).exists()
    print('FRIENDS: ', friends)
    return render(request, 'accounts/others_profile.html', {'innovator': innovator, 'innovator_skills': innovator_skills, 'innovator_services': innovator_services, 'projects': projects, 'conn_request': conn_request,  'conn_already_sent': conn_request.exists(), 'friends': friends})

def edit_profile(request):
    user = BaseUser.objects.get(username=request.user.username)
    try:
        innovator = Innovator.objects.get(user__username=request.user.username)
    except Innovator.DoesNotExist:
        return HttpResponse('You are unable to access this page because you are not an innovator.')
    user = BaseUser.objects.get(username=request.user.username)
    user_info = BaseUser.objects.get(username=request.user.username)
    if not request.user.is_authenticated:
        return redirect('accounts:innovator_login')
    # USER ABOUT ME
    # if request.method == 'POST' and 'user_about_me' in request.POST:
    #     about_me_form = UpdateAboutMeForm(request.POST, instance=request.user)
    #     if about_me_form.is_valid():
    #         obj = about_me_form.save(commit=False)
    #         if about_me_form.cleaned_data['about_me']:
    #             obj.about_me = about_me_form.cleaned_data['about_me']
    #         obj.save()
    #         print('OBJ: ', obj.about_me)
    #         return redirect('accounts:profile')
    #     else:
    #         print(about_me_form.errors.as_data())
    # else:
    #     about_me_form = UpdateAboutMeForm(instance=request.user, initial={
    #         "about_me": Innovator.objects.get(user__username=request.user.username).about_me
    #     })

    
    # USER PERSONAL DATA
    if request.method == 'POST' and 'user_p_form' in request.POST:
        user_p_data = {
            'about_me': request.POST.get('about_me'),
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_name': request.POST.get('middle_name'),
            'pfp': request.POST.get('pfp'),
            'phone_num': request.POST.get('phone_num'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'bio': request.POST.get('bio'),
            'job_title': request.POST.get('job_title'),
        }
        user_p_info = UpdatePersonalProfileForm(user_p_data, request.FILES, instance=request.user)
        if user_p_info.is_valid():
            user_obj = user_p_info.save(commit=False)
            if user_p_info.cleaned_data['pfp']:
                user_obj.pfp = user_p_info.cleaned_data['pfp']
            if user.date_of_birth:
                user_obj.date_of_birth = user.date_of_birth
            if user_p_info.cleaned_data['about_me']:
                user_obj.about_me = user_p_info.cleaned_data['about_me']
            user_obj.save()
            
            return redirect('accounts:profile')
        else:
            print(user_p_info.errors.as_data())
    else:
        user_p_info = UpdatePersonalProfileForm(
            instance=request.user,
            initial= {
                'about_me': user.about_me,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'middle_name': user.middle_name,
                'pfp': user.pfp,
                'phone_num': user.phone_num,
                'date_of_birth': user.date_of_birth,
                'bio': user.bio
            }
        )


    # KNOWLEDGE-BASED QUESTION
    if request.method == 'POST' and 'kba_question' in request.POST:
        kba_question = request.POST.get('kba_question')
        answer = request.POST.get('answer')
        print('brev_man')
        kba_data = {
            'kba_question': kba_question,
            'answer': answer
        }
        kba_form = UpdateKBAQuestionForm(kba_data, instance=request.user)
        if kba_form.is_valid():
            KBAQuestion.objects.create(
                kba_question= kba_question,
                answer=answer,
                user=user
            )
            messages.success(request, 'Knowledge-based Question successfully updated.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Knowledge-based Question could not be updated.')
    else:
        kba_form = UpdateKBAQuestionForm(
            instance=request.user, 
            initial= {
                'kba_question': request.POST.get('kba'),
                'answer': request.POST.get('answer')
            }
        )

    # USER NIN DATA
    if request.method == 'POST' and 'nin' in request.POST:
        print('YES BRO')
        nin = request.POST.get('nin', '').strip()
        nin_data = {
            'nin': nin
        }
        user_nin_info = UpdateUserNINForm(nin_data, instance=request.user)
        if user_nin_info.is_valid():
            url = "https://api.verified.africa/sfx-verify/v3/id-service/"
            # 02730846093
            payload = {
                "searchParameter": nin,
                "verificationType": "NIN-SEARCH"
            }
            headers = {
                "accept": "application/json",
                "userid": "1628022119761",
                "apiKey": "KC69ZuFxVEsSpld69koD",
                "content-type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            print('BRO DAYUM')
            if response.json()['description'].lower() == "success":
                user_nin_info.save()
                print('DONE MAN')
                messages.success(request, 'NIN is valid. ✅')
                return JsonResponse(response.json(), status=200)
                # return redirect('accounts:profile')
            else:
                messages.error(request, f"No NIN record found for '{nin}'")
                return redirect('accounts:edit_profile')
            print(response.text)
            # user_nin_info.save()
    else:
        user_nin_info = ''
        if user.nin:
            user_nin_info = UpdateUserNINForm(
                instance=request.user,
                initial= {
                    'nin': user.nin.strip()
                }
            )
#   USER RESIDENTIAL DATA
    if request.method == 'POST' and 'user_r_form' in request.POST:
        user_r_data = {
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'country': request.POST.get('country'),
            'address': request.POST.get('address'),
            'zipcode': request.POST.get('zipcode')
        }
        user_r_info = UpdateUserResidentialInfoForm(user_r_data, instance=request.user)
        if user_r_info.is_valid():
            user_r_info.save()
            return redirect('accounts:profile')
        else:
            print(user_r_info.errors.as_data())
    else:
        user_r_info = UpdateUserResidentialInfoForm()
    
#   USER SKILS DATA
    if request.method == 'POST' and 'user_skill_form' in request.POST:
        context = {}
        skill_form = UpdateUserSkillsForm(request.POST)
        if skill_form.is_valid():
            if not InnovatorSkill.objects.filter(skill=request.POST.get('skill'), innovator__user__pk=request.user.pk).exists():
                if skill_form.cleaned_data.get('skill'):
                    if InnovatorSkill.objects.filter(innovator__user__pk=request.user.pk).count() < 5:
                        skill_obj = skill_form.save(commit=False)
                        skill_obj.innovator = Innovator.objects.get(user__username=request.user.username)
                        skill_obj.save()
                        return redirect('accounts:profile')
                    else:
                        messages.error(request, 'You can only add a maximum of 5 skills')
            else:
                skill_form.add_error('skill', 'This skill already exists.')
        else:
            print('SKILLS ERRORS: ', skill_form.errors)
    else:
        skill_form = UpdateUserSkillsForm()

#   USER SOCIALS DATA
    if request.method == 'POST' and 'user_s_form' in request.POST:
        user_s_data = {
            'facebook': request.POST.get('facebook'),
            'linkedin': request.POST.get('linkedin'),
            'twitter': request.POST.get('twitter'),
            'instagram': request.POST.get('instagram'),
            'website': request.POST.get('website')
        }
        user_s_info = UpdateUserSocialsForm(user_s_data, instance=request.user)
        if user_s_info.is_valid():
            user_s_info.save()
            return redirect('accounts:profile')
        else:
            print(user_s_info.errors.as_data())
    else:
        user_s_info = UpdateUserSocialsForm()

#   USER CHANGE PASSWORD DATA
    user = request.user
    if request.method == 'POST' and 'password_change' in request.POST:
        change_password_form = ChangePasswordForm(user, request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
            return redirect('accounts:edit_profile')
        else:
            print('ERRORS: ', change_password_form.errors.as_data())
    else:
        change_password_form = ChangePasswordForm(user)

#   USER SERVICES DATA
    if request.method == 'POST' and 'service_form' in request.POST:
        service_form = UpdateUserServiceForm(request.POST)
        if service_form.is_valid():
            if not Service.objects.filter(service=service_form.cleaned_data.get('service')).exists():
                if service_form.cleaned_data.get('service'):
                    if Innovator.objects.get(user__username=request.user.username).service_set.all().count() < 5:
                        service_obj = service_form.save(commit=False)
                        service_obj.user = BaseUser.objects.get(username=request.user.username)
                        service_obj.save()
                    else:
                        messages.error(request, 'You can only add a maximum of 5 services')
            else:
                service_form.add_error('service', 'This skill already exists.')
        else:
            print('SERVICES FORM ERRORS: ', service_form.errors.as_data())
    else:
        service_form = UpdateInnovatorServicesForm()

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user,
        'user': user,
        'user_p_info_form': user_p_info,
        'user_r_info_form': user_r_info,
        'user_s_info_form': user_s_info,
        'kba_form': kba_form,
        'user_nin_info': user_nin_info,
        'change_password_form': change_password_form,
        'user_skill_form': skill_form,
        'user_skills': Innovator.objects.get(user__username=request.user).innovatorskill_set.all(),
        'user_services': Innovator.objects.get(user__username=request.user).service_set.all(),
        'user_service_form': service_form,
        'innovator': Innovator.objects.get(user__username=request.user.username),
        'kba': len(KBAQuestion.objects.filter(user__username=request.user.username))
    })

def moderator_edit_profile(request):
    try:
        user = Moderator.objects.get(user__username=request.user.username)
    except:
        return redirect('accounts:moderator_login')
    try:
        moderator = Moderator.objects.get(user__username=request.user.username)
    except Moderator.DoesNotExist:
        return HttpResponse('You are unable to access this page because you are not an innovator.')
    user = Moderator.objects.get(user__username=request.user.username)
    user_info = Moderator.objects.get(user__username=request.user.username)
    if not request.user.is_authenticated:
        return redirect('accounts:moderator_login')
    
        # USER PERSONAL DATA
    if request.method == 'POST' and 'user_p_form' in request.POST:
        print('YOOOOO: ', request.POST.get('job_title'))
        user_p_data = {
            'about_me': request.POST.get('about_me'),
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_name': request.POST.get('middle_name'),
            'pfp': request.POST.get('pfp'),
            'phone_num': request.POST.get('phone_num'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'bio': request.POST.get('bio'),
            'job_title': request.POST.get('job_title'),
        }
        user_p_info = UpdatePersonalProfileForm(user_p_data, request.FILES, instance=request.user)
        if user_p_info.is_valid():
            user_obj = user_p_info.save(commit=False)
            if user_p_info.cleaned_data['pfp']:
                user_obj.pfp = user_p_info.cleaned_data['pfp']
            if user_p_info.cleaned_data['date_of_birth']:
                user_obj.date_of_birth = user_p_info.cleaned_data['date_of_birth']
            if user_p_info.cleaned_data['about_me']:
                user_obj.about_me = user_p_info.cleaned_data['about_me']
            
            user_obj.save()
            print('BREVVVVVVVV', user_obj.job_title)
            return redirect('accounts:mod_profile')
        else:
            print(user_p_info.errors.as_data())
    else:
        user_p_info = UpdatePersonalProfileForm()

#   USER RESIDENTIAL DATA
    if request.method == 'POST' and 'user_r_form' in request.POST:
        user_r_data = {
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'country': request.POST.get('country'),
            'address': request.POST.get('address'),
            'zipcode': request.POST.get('zipcode')
        }
        user_r_info = UpdateUserResidentialInfoForm(user_r_data, instance=request.user)
        if user_r_info.is_valid():
            user_r_info.save()
            return redirect('accounts:mod_profile')
        else:
            print(user_r_info.errors.as_data())
    else:
        user_r_info = UpdateUserResidentialInfoForm()

#   USER SOCIALS DATA
    if request.method == 'POST' and 'user_s_form' in request.POST:
        user_s_data = {
            'facebook': request.POST.get('facebook'),
            'linkedin': request.POST.get('linkedin'),
            'twitter': request.POST.get('twitter'),
            'instagram': request.POST.get('instagram'),
            'website': request.POST.get('website')
        }
        user_s_info = UpdateUserSocialsForm(user_s_data, instance=request.user)
        if user_s_info.is_valid():
            user_s_info.save()
            return redirect('accounts:mod_profile')
        else:
            print(user_s_info.errors.as_data())
    else:
        user_s_info = UpdateUserSocialsForm()

#   USER CHANGE PASSWORD DATA
    user = request.user
    if request.method == 'POST' and 'password_change' in request.POST:
        change_password_form = ChangePasswordForm(user, request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
            return redirect('accounts:mod_edit_profile')
        else:
            print('ERRORS: ', change_password_form.errors.as_data())
    else:
        change_password_form = ChangePasswordForm(user)

#   USER SERVICES DATA
    if request.method == 'POST' and 'service_form' in request.POST:
        service_form = UpdateUserServiceForm(request.POST)
        if service_form.is_valid():
            if not Service.objects.filter(service=service_form.cleaned_data.get('service')).exists():
                if service_form.cleaned_data.get('service'):
                    if Moderator.objects.get(user__username=request.user.username).service_set.all().count() < 5:
                        service_obj = service_form.save(commit=False)
                        service_obj.user = Moderator.objects.get(user__username=request.user.username)
                        service_obj.save()
                    else:
                        messages.error(request, 'You can only add a maximum of 5 services')
            else:
                service_form.add_error('service', 'This skill already exists.')
        else:
            print('SERVICES FORM ERRORS: ', service_form.errors.as_data())
    else:
        service_form = UpdateInnovatorServicesForm()

    return render(request, 'accounts/mod_edit_profile.html', {
        'user_form': user,
        'user': user,
        'user_p_info_form': user_p_info,
        'user_r_info_form': user_r_info,
        'user_s_info_form': user_s_info,
        'change_password_form': change_password_form,
        # 'user_skills': Moderator.objects.get(user__username=request.user).innovatorskill_set.all(),
        'user_services': Service.objects.filter(user=request.user.pk),
        'user_service_form': service_form,
        'moderator': Moderator.objects.get(user__username=request.user.username)
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

def remove_pfp(request):
    user = BaseUser.objects.get(username=request.user.username)
    if user.pfp:
        user.pfp.delete(save=True)
        bool= True
    else:
        bool = False
    return JsonResponse(bool, safe=False)

def remove_skill(request, skill_id):
    skill = InnovatorSkill.objects.get(skill_id=skill_id)
    skill.delete()
    return redirect('accounts:edit_profile')

def remove_service(request, pk):
    service = Service.objects.get(pk=pk)
    service.delete()
    return redirect('accounts:edit_profile')


@login_required
def follow(request, username, option):
    user = request.user.username
    following = get_object_or_404(BaseUser, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
        else:
            pass
            
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    except BaseUser.DoesNotExist:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def error404View(request):
    return render(request, 'base/404.html')

def payment(request):
    return redirect('accounts:make_payment')
    # return render(request, 'accounts/payment.html')

def send_connection_request(request, recipient_pk):
    recipient = get_object_or_404(Innovator, pk=recipient_pk)
    requester = get_object_or_404(Innovator, user__pk=request.user.pk)

    if recipient == requester:
        messages.info(request, mark_safe('You can not send a connection request to yourself.'))
    else:
        if ConnectionRequest.objects.filter(
            requester = requester,
            recipient = recipient,
            remote_response = False,
            recipient_has_responded=False
        ).exists():
            messages.info(request, mark_safe('You have already sent a connection request to this user.<br/>Kindly wait for their response.'))
        else:
            if ConnectionRequest.objects.filter(
                        requester = requester,
                        recipient = recipient,
                        remote_response = True,
                        are_friends = False
                    ).exists() or ConnectionRequest.objects.filter(
                        requester = requester,
                        recipient = recipient,
                        recipient_has_responded=True,
                        are_friends=False
                    ).exists():
                conn_request = ConnectionRequest.objects.get(
                                    requester = requester,
                                    recipient = recipient,
                                    are_friends=False)
                conn_request.recipient_has_responded = False
                conn_request.remote_response  = False
                conn_request.save(update_fields=['recipient_has_responded', 'remote_response'])
            else:
                
                ConnectionRequest.objects.create(
                    recipient=recipient,
                    requester=requester,
                )
            messages.success(request, 'Connection Request sent. Kindly wait for their response.')
            return redirect('accounts:profile_with_arg', recipient_pk)
    return render(request, 'accounts/others_profile.html')

def friend_requests(request):
    friend_requests = ConnectionRequest.objects.filter(
        recipient__user__pk=request.user.pk,
        recipient_has_responded=False,
        are_friends=False,
        remote_response=False,
    )
    return render(request, 'accounts/friend_requests.html', {'friend_requests': friend_requests})

@login_required
def accept_conn_request(request, conn_request_pk):
    conn_request = ConnectionRequest.objects.get(pk=conn_request_pk)
    if conn_request.recipient.user.pk == request.user.pk:
        if conn_request.recipient_has_responded == False and conn_request.remote_response == False:
            conn_request.is_accepted = True
            conn_request.recipient_has_responded = True
            conn_request.are_friends = True
            conn_request.save(update_fields=['is_accepted', 'recipient_has_responded', 'are_friends'])

            if ConnectionRequest.objects.filter(
                requester__pk=conn_request.recipient.pk, recipient__pk=conn_request.requester.pk,
                recipient_has_responded=False,
                are_friends=False
                ).exists():
                conn_request_2 = ConnectionRequest.objects.get(
                    requester__pk=conn_request.recipient.pk, recipient__pk=conn_request.requester.pk,
                    recipient_has_responded=False,
                    are_friends=False
                    )
                conn_request_2.is_accepted = True
                conn_request_2.are_friends = True
                conn_request_2.remote_response = True
                conn_request_2.save(update_fields=['is_accepted', 'are_friends', 'remote_response'])
            Connection.objects.create(
                user1=conn_request.recipient,
                user2=conn_request.requester,
                conn_request=conn_request
            )
            return JsonResponse(data={'status': 'success'})
        return HttpResponse('You have already responded to the request.')
    return HttpResponse('You do not have the privilege to view this page.')


@login_required
def decline_conn_request(request, conn_request_pk):
    conn_request = ConnectionRequest.objects.get(pk=conn_request_pk)
    if conn_request.recipient.user.pk == request.user.pk:
        if not conn_request.recipient_has_responded and conn_request.remote_response == False:
            conn_request.is_accepted = False
            conn_request.recipient_has_responded = True
            conn_request.save(update_fields=['is_accepted', 'recipient_has_responded'])

            conn_request_2 = ConnectionRequest.objects.get(
                requester__pk=conn_request.recipient.pk, recipient__pk=conn_request.requester.pk,
                recipient_has_responded=False,
                are_friends=False
                )
            conn_request_2.remote_response = True
            conn_request_2.save(update_fields=['remote_response'])

            return JsonResponse(data={'status': 'success'})
        return HttpResponse('You have already responded to the request.')
    return HttpResponse('You do not have the privilege to view this page.')

@login_required
def friends_list(request):
    return render(request, 'core/friends-list.html')