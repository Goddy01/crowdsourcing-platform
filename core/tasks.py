from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from .views import send_funding_completed_email, send_milestone_email, send_project_approval_status, pay_investors, send_money_recipient_email, send_money_2, notify_investors_of_project_fund_withdrawal
from celery.utils.log import get_task_logger
from accounts.models import Innovator
from crowdsourcing import settings


logger = get_task_logger(__name__)
from_email = settings.EMAIL_HOST_USER


@shared_task
def send_funding_completed_email_task(**kwargs):
    investment_pk = kwargs.get('investment_pk')
    logger.info('FUNDING GOAL REACHED EMAIL SENT')
    return send_funding_completed_email(investment_pk)


@shared_task
def send_milestone_email_task(**kwargs):
    investment_pk = kwargs.get('investment_pk')
    current_site = kwargs.get('current_site')
    milestone_pk = kwargs.get('milestone_pk')
    type = kwargs.get('type')
    logger.info('MILESTONE EMAIL SENT')
    return send_milestone_email(investment_pk=investment_pk, current_site=current_site, milestone_pk=milestone_pk, type=type)


@shared_task
def send_project_approval_status_task(**kwargs):
    investment_pk = kwargs.get('investment_pk')
    logger.info('PROJECT APPROVAL STATUS EMAIL SENT')
    return send_project_approval_status(investment_pk)

@shared_task
def pay_investors_task(**kwargs):
    investment_pk = kwargs.get('investment_pk')
    logger.info('PAYMENT OF INVESTORS INITIATED')
    return pay_investors(investment_pk=investment_pk)

@shared_task
def send_money_recipient_email_task(**kwargs):
    send_money = kwargs.get('send_money')
    return send_money_recipient_email(send_money)

@shared_task
def send_money_task(**kwargs):
    amount_to_send = kwargs.get('amount_to_send')
    sender_pk = kwargs.get('sender_pk')
    recipient_pk = kwargs.get('recipient_pk')
    sender_prebalance = kwargs.get('sender_prebalance')
    sender_postbalance = kwargs.get('sender_postbalance')
    domain = kwargs.get('domain')
    return send_money_2(amount_to_send, sender_pk, recipient_pk, sender_prebalance, sender_postbalance, domain)

@shared_task
def notify_investors_of_project_fund_withdrawal_task(**kwargs):
    withdrawal_pk = kwargs.get('withdrawal_pk')
    return notify_investors_of_project_fund_withdrawal(withdrawal_pk)

@shared_task
def notify_account_verification_task(innovator_pk):
    innovator = Innovator.objects.get(pk=innovator_pk)
    subject = f"Hurray!!! Your Innovator Account Has Been Verified"
    html_message = render_to_string(
        'accounts/innovator-account-verified.html', {
            'user': innovator.user
        }
    )
    send_mail(subject, message=strip_tags(html_message), recipient_list=[f"{innovator.user.email}"], fail_silently=False, html_message=html_message)

@shared_task
def notify_account_unverification_task(innovator_pk):
    innovator = Innovator.objects.get(pk=innovator_pk)
    subject = f"Oops. Your Verification Has Been Suspended"
    html_message = render_to_string(
        'accounts/innovator-account-unverified.html', {
            'user': innovator.user
        }
    )
    send_mail(subject, message=strip_tags(html_message), recipient_list=[f"{innovator.user.email}"], fail_silently=False, html_message=html_message)