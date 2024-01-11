from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .views import send_funding_completed_email
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def send_funding_completed_email_task(investment_pk):
    logger.info('FUNDING GOAL REACHED EMAIL SENT')
    return send_funding_completed_email(investment_pk)