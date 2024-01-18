from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from celery.utils.log import get_task_logger
from accounts.models import Innovator, BaseUser
from crowdsourcing import settings


logger = get_task_logger(__name__)
from_email = settings.EMAIL_HOST_USER


@shared_task
def notify_account_verification_task(user_pk):
    user = BaseUser.objects.get(pk=user_pk)
    subject = f"Hurray!!! Your Innovator Account Has Been Verified"
    html_message = render_to_string(
        'accounts/innovator-account-verified.html', {
            'user': user
        }
    )
    send_mail(subject, message=strip_tags(html_message), recipient_list=[f"{user.email}"], fail_silently=False, html_message=html_message, from_email=from_email)

@shared_task
def notify_account_unverification_task(user_pk):
    user = BaseUser.objects.get(pk=user_pk)
    subject = f"Oops. Your Verification Has Been Suspended"
    html_message = render_to_string(
        'accounts/innovator-account-unverified.html', {
            'user': user
        }
    )
    send_mail(subject, message=strip_tags(html_message), recipient_list=[f"{user.email}"], fail_silently=False, html_message=html_message, from_email=from_email)