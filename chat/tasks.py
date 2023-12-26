from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .views import send_new_group_msg_email_alert
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def send_new_group_msg_email_alert_task(new_message, sender, domain, recipient_list, html_message, subject, from_email):
    logger.info('NEW GROUP MSG EMAIL ALERT SENT')
    return send_new_group_msg_email_alert(new_message=new_message, sender = sender, domain = domain, recipient_list = recipient_list, html_message=html_message, subject=subject, from_email=from_email)