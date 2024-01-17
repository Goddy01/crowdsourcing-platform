from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .views import send_funding_completed_email, send_milestone_email, send_project_approval_status, pay_investors, send_money_recipient_email, send_money_2, notify_investors_of_project_fund_withdrawal
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

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