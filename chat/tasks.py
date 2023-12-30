from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .views import send_new_group_msg_email_alert, send_friend_new_msg_alert
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def send_new_group_msg_email_alert_task(new_message, sender, domain, **kwargs):
    get_group_members_emails = kwargs.get('get_group_members_emails', None)
    content_type = kwargs.get('content_type')
    logger.info('NEW GROUP MSG EMAIL ALERT SENT')
    return send_new_group_msg_email_alert(new_message=new_message, sender = sender, domain = domain, get_group_members_emails=get_group_members_emails, content_type=content_type)

@shared_task
def send_friend_new_msg_email_alert_task(new_message, sender, domain, **kwargs):
    recipient = kwargs.get('recipient')
    content_type = kwargs.get('content_type')
    recipient = kwargs.get('recipient')
    logger.info('FRIEND NEW MSG EMAIL ALERT SENT')
    return send_friend_new_msg_alert(new_message=new_message, sender = sender, domain = domain, content_type=content_type, recipient=recipient)