from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mass_mail, send_mail
from accounts.models import BaseUser, Innovator
from itertools import chain
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.decorators import login_required
from accounts.models import Connection, Innovator
from .models import Chat, Group, GroupChat
from django.core.serializers import serialize
from django.conf import settings
from django.http import HttpResponse

from_email = settings.EMAIL_HOST_USER

def index(request):
    return render(request, 'chat/chat.html')

@login_required
def room(request, room_name=None):
    if request.user.is_moderator:
        return HttpResponse('Chat feature for moderators is coming soon!!!')
    if room_name is not None:
        room_name = mark_safe(json.dumps(room_name))
    user = Innovator.objects.get(user__username=request.user.username)
    friends_list = Connection.objects.filter(
        Q(user1=user) | Q(user2=user)
    )
    conversations = []

    return render(request, 'chat/room.html', {
        'username': request.user.username,
        'room_name_json': room_name,
        'friends': conversations,
        'friends_list': friends_list,
        'groups': Group.objects.filter(members=user.user.pk),
        'groups2': serialize('json', queryset=Group.objects.filter(members=user.user.pk)),
        'user':user
    })


def get_messages(sender, recipient):
    qs1 = Chat.objects.filter(sender__username=sender, recipient__username=recipient)
    qs2 = Chat.objects.filter(sender__username=recipient, recipient__username=sender)

    return qs1 | qs2

def get_group_messages(logged_in_user, group_pk):
    group = Group.objects.get(pk=group_pk)
    logged_in_user = BaseUser.objects.get(username=logged_in_user)
    if logged_in_user in group.members.all():
        return GroupChat.objects.filter(group=group)

# def set_all_message_to_seen(request, sender, recipient):
#     messages = Chat.objects.filter(
#         sender__username=sender,
#         recipient__username=recipient,
#         is_seen=False
#     )
#     for m in messages:
#         m.is_seen = True
#         m.save(update_fields=['is_seen'])
#     return JsonResponse(data = {'status': 'success'})

# @login_required

def get_group_members(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    
    # Select specific fields for each member
    members = group.members.all().values('first_name', 'last_name', 'middle_name', 'pfp', 'username')

    return JsonResponse({'members': list(members)})

def send_file_message(request, sender, recipient, parent_message=None):
    if request.method == "POST" and request.FILES.get("file"):
        sender = BaseUser.objects.get(username=sender)
        recipient = BaseUser.objects.get(username=recipient)
        file = request.FILES['file']
        if parent_message is None:
            message  = Chat.objects.create(
                sender=sender,
                recipient=recipient,
                file_content=file
            )
        if parent_message is not None:
            message_tagged = Chat.objects.get(pk=parent_message)
            
            message  = Chat.objects.create(
                sender=sender,
                recipient=recipient,
                file_content=file,
                message_tagged = message_tagged
            )
    return JsonResponse(data = 
        {
        'status': 'success', 
        'file_url': message.file_content.url, 
        'message_sender': message.sender.username, 
        'message_sender_pfp_url': message.sender.pfp.url, 
        'message_recipient': message.recipient.username, 
        'message_recipient_url': message.recipient.pfp.url, 
        'timestamp': message.timestamp
        })


def send_group_file_message(request, sender, group_pk, parent_message=None):
    if request.method == "POST" and request.FILES.get("file"):
        sender = BaseUser.objects.get(username=sender)
        group = Group.objects.get(pk=group_pk)
        file = request.FILES['file']
        if parent_message is None:
            message  = GroupChat.objects.create(
                sender=sender,
                group=group,
                file_content=file
            )
        if parent_message is not None:
            message_tagged = GroupChat.objects.get(pk=parent_message)
            message  = GroupChat.objects.create(
                sender=sender,
                group=group,
                file_content=file,
                message_tagged = message_tagged
            )
    return JsonResponse(data = 
        {
        'status': 'success', 
        'file_url': message.file_content.url, 
        'message_sender': message.sender.username, 
        'groupPk': message.group.pk, 
        'timestamp': message.timestamp
        })

def sender_profile(request, sender_username):
    innovator_pk = Innovator.objects.get(user__username=sender_username).pk
    return redirect('accounts:profile_with_arg', innovator_pk)

def send_friend_new_msg_alert(new_message, sender, domain, content_type, recipient, recipient_fullname, sender_fullname):
    html_message = None
    recipient_fullname = recipient_fullname
    sender_fullname = sender_fullname
    subject = f"New message from your friend, {sender}"
    if content_type == 'text':
        html_message = render_to_string(
            'chat/friend_new_msg_notif.html', {
            'sender': sender,
            'domain': domain,
            'recipient_list': [recipient],
            'recipient_fullname': recipient_fullname,
            'sender_fullname': sender_fullname,
            'date_received': new_message['timestamp'],
            'message': new_message,
            'content': new_message['content'],
            'type': 'normal',
            'content_type': 'text'
            }
        )
    elif content_type == 'file':
        html_message = render_to_string(
            'chat/friend_new_msg_notif.html', {
            'sender': sender,
            'domain': domain,
            'recipient_list': [recipient],
            'recipient_fullname': recipient_fullname,
            'sender_fullname': sender_fullname,
            'date_received': new_message['timestamp'],
            'message': new_message,
            'content': new_message['content'],
            'type': 'normal',
            'content_type': 'file'
            }
        )
    send_mail(subject=subject, message='', html_message=html_message, from_email=from_email, recipient_list=[recipient], fail_silently=False)

def send_new_group_msg_email_alert(new_message, sender, domain, get_group_members_emails, content_type):
    recipient_list = get_group_members_emails
    mail_group_name = new_message['group_name']
    content = new_message['content']
    file_content = None
    content_type = content_type

    subject = f"New Message from {mail_group_name}"
    logged_in_user = new_message['logged_in_user']
    
    for recipient in recipient_list:
        recipient_obj = BaseUser.objects.get(email=recipient)
        recipient_username = recipient_obj.username.lower()
        if recipient_obj.receive_msg_email_notif:
            if content_type == 'text':
                if f'@{recipient_username}' not in content.lower():
                    html_message = render_to_string(
                        'chat/new_msg_notif.html', {
                        'sender': sender,
                        'domain': domain,
                        'recipient_list': recipient,
                        'date_received': new_message['timestamp'],
                        'message': new_message,
                        'group_name': mail_group_name,
                        'content': content,
                        'logged_in_user': logged_in_user,
                        'type': 'normal',
                        'content_type': 'text'
                        }
                    )
                    send_mail(subject=subject, message='', html_message=html_message, from_email=from_email, recipient_list=[recipient], fail_silently=False)
                elif f'@{recipient_username}' in content.lower():
                    username_index = content.lower().find(f'@{recipient_username}')
                    username_index += (len(f'@{recipient_username}') - 1)

                    # Check if the username is followed by a space or it is at the end of the string
                    if username_index + 1 == len(content) or content[username_index + 1] == ' ':
                        html_message = render_to_string(
                            'chat/new_msg_notif.html', {
                                'sender': sender,
                                'domain': domain,
                                'recipient_list': recipient,
                                'date_received': new_message['timestamp'],
                                'message': new_message,
                                'group_name': mail_group_name,
                                'content': content,
                                'logged_in_user': logged_in_user,
                                'type': 'normal',
                                'content_type': 'text'
                            }
                        )
                        send_mail(subject=subject, message='', html_message=html_message, from_email=from_email, recipient_list=[recipient], fail_silently=False)
                    else:
                        html_message = render_to_string(
                            'chat/new_msg_notif.html', {
                                'sender': sender,
                                'domain': domain,
                                'recipient_list': recipient,
                                'date_received': new_message['timestamp'],
                                'message': new_message,
                                'group_name': mail_group_name,
                                'content': content,
                                'logged_in_user': logged_in_user,
                                'type': 'normal',
                                'content_type': 'text'
                            }
                        )
                        send_mail(subject=subject, message='', html_message=html_message, from_email=from_email, recipient_list=[recipient], fail_silently=False)

            elif content_type == 'file':
                html_message = render_to_string(
                            'chat/new_msg_notif.html', {
                            'sender': sender,
                            'domain': domain,
                            'recipient_list': recipient,
                            'date_received': new_message['timestamp'],
                            'message': new_message,
                            'group_name': mail_group_name,
                            'logged_in_user': logged_in_user,
                            'type': 'normal',
                            'content_type': 'file'
                            }
                        )
                send_mail(subject=subject, message='', html_message=html_message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)