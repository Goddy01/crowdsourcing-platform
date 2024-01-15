from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .views import send_funding_completed_email, send_milestone_email, send_project_approval_status, pay_investors
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
    request = kwargs.get('request')
    investment_pk = kwargs.get('investment_pk')
    logger.info('PAYMENT OF INVESTORS INITIATED')
    return pay_investors(request=request, investment_pk=investment_pk)