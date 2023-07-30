from django.http import HttpResponseRedirect
from django.urls import reverse
import urllib
from .models import Innovator

# This is initially from https://github.com/python-social-auth/social-core/blob/master/social_core/pipeline/user.py
def get_username(strategy, details, backend, user=None, *args, **kwargs):
    # Get the logged in user (if any)
    logged_in_user = strategy.storage.user.get_username(user)

    # Custom: check for email being provided
    # if not details.get('email'):
    #     error = "Sorry, but your social network (Facebook or Google) needs to provide us your email address."
    #     return HttpResponseRedirect("?error=" + urllib.quote_plus(error))

    # # Custom: if user is already logged in, double check his email matches the social network email
    # if logged_in_user:
    #     if logged_in_user.lower() != details.get('email').lower():
    #         error = "Sorry, but you are already logged in with another account, and the email addresses do not match. Try logging out first, please."
    #         return HttpResponseRedirect("?error=" + urllib.quote_plus(error))

    return {
        'username': details.get('email').lower(),
    }

def save_profile(backend, user, response, *args, **kwargs):
    # if Innovator.objects.filter(user_id=user.id).count() == 0 :
    Innovator = Innovator.objects.create(
        is_project_mgr=True, 
        user=user, 
        # user__signup_confirmation=True
        )
        # your logic for new fields 
        # Innovator.save()