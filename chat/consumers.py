import json
from urllib.parse import urlparse
from django.db.models import Q
from .views import send_new_group_msg_email_alert
from django.template.loader import render_to_string
from .tasks import send_new_group_msg_email_alert_task, send_friend_new_msg_email_alert_task
from django.utils.html import strip_tags
from django.core.mail import send_mass_mail, send_mail
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer, SyncConsumer
from .models import Chat, GroupChat, Group
from accounts.models import BaseUser
from .views import get_messages, get_group_messages, get_group_members
from django.shortcuts import get_object_or_404
from django.conf import settings


from_email = settings.EMAIL_HOST_USER

class ChatConsumer(WebsocketConsumer):
    def send_email_in_consumer(self, new_message, sender, content_type):
        header_tuple = self.scope.get('headers', [])[0]
        address = header_tuple[1].decode('utf-8')
        ip_address, port = address.split(':')
        domain = f"{ip_address}:{port}"
        
        serialized_message = {
            'id': new_message.id,
            'sender_username': new_message.sender.username,
            'recipient': new_message.recipient.email,
            'content': new_message.content,
            'timestamp': str(new_message.timestamp),
            'logged_in_user': self.scope['user'].email,
            # Add other fields as needed
        }

        # Pass only the necessary information to Celery
        task = send_friend_new_msg_email_alert_task.apply_async(
                kwargs={
                    'new_message': serialized_message,
                    'sender': serialized_message['sender_username'],
                    'domain': domain,
                    'recipient': serialized_message['recipient'],
                    'content_type': content_type,
                    'recipient_fullname': new_message.recipient.get_full_name(),
                    'sender_fullname': new_message.sender.get_full_name()
                },
                countdown=15
            )
    def fetch_messages(self, data):
        sender = BaseUser.objects.get(username=data['sender'])
        recipient = BaseUser.objects.get(username=data.get('recipient'))
        logged_in_user = BaseUser.objects.get(username=self.scope['user'].username)
        if logged_in_user == sender:
            messages = get_messages(sender=sender, recipient=recipient)
            content = {
                'command': 'messages',
                'messages': self.messages_to_json(messages)
            }
        else:
            content = {}
        self.send_message(content)

    def new_file_message(self, data):
        content = {}
        sender = BaseUser.objects.get(username=data['sender'])
        recipient = BaseUser.objects.get(username=data['recipient'])
        message = Chat.objects.filter(sender=sender, recipient=recipient, file_content__isnull=False).order_by('-timestamp').first()
        if data['message_type'] == 'normal':
            content = {
            'command': 'new_file_normal',
            'message': self.message_to_json(message)
                }

        elif data['message_type'] == 'tagged':
            content = {
                'command': 'new_file_tagged',
                'message': self.tagged_message_to_json(message)
            }
        if recipient.receive_msg_email_notif:
            self.send_email_in_consumer(message, sender.get_full_name(), 'file')
        return self.send_chat_message(content)

    def new_message(self, data):
        content = {}
        sender = data['from']
        sender_user = BaseUser.objects.get(username=sender)
        recipient = BaseUser.objects.get(username=data['to'])
        message = None
        if data['type'] == 'normal':
            message = Chat.objects.create(
                sender=sender_user,
                recipient=recipient,
                content=data['message']
            )
            content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }

        elif data['type'] == 'tagged':
            parent_message = data['parentMessage']
            message = data['message']
            message_tagged = Chat.objects.get(pk=parent_message)
            message = Chat.objects.create(
                message_tagged = message_tagged,
                sender = sender_user,
                recipient = recipient,
                content = message
            )
            content = {
                'command': 'tag_message',
                'message': self.tagged_message_to_json(message)
            }
        if recipient.receive_msg_email_notif:
            self.send_email_in_consumer(message, sender_user.get_full_name(), 'text')
        return self.send_chat_message(content)
    
    def tag_message(self, data):
        sender = data['sender']
        recipient = data['recipient']
        parent_message = data['parentMessage']
        message = data['message']
        message_tagged = get_object_or_404(Chat, pk=parent_message['pk'])
        message = Chat.objects.create(
            message_tagged = message_tagged,
            sender = sender,
            recipient = recipient,
            content = message
        )
        content = {
            'command': 'tag_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)
    
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            if message.message_tagged is not None:
                result.append(
                    self.tagged_message_to_json(message)
                )
            elif message.message_tagged is None:
                
                result.append(
                    self.message_to_json(message)
                )
        return result
    def message_to_json(self, message):
        try:
            file_content = message.file_content.url
        except:
            file_content = None
        if message.content is not None:
            content = message.content
        else:
            content = None
        return {
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'content': content,
            'timestamp': str(message.timestamp),
            'sender_pfp_url': message.sender.pfp.url,
            'file_content': file_content,
            'pk': message.pk,

        }
    
    def tagged_message_to_json(self, message):
        try:
            file_content = message.file_content.url
        except:
            file_content = None
        if message.content is not None:
            content = message.content
        else:
            content = None


        try:
            tagged_file_content = message.message_tagged.file_content.url
        except:
            tagged_file_content = None
        try :
            tagged_content = message.message_tagged.content
        except:
            tagged_content = None
        return {
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'content': content,
            'timestamp': str(message.timestamp),
            'sender_pfp_url': message.sender.pfp.url,
            'file_content': file_content,
            'pk': message.pk,
            'tagged_pk': message.message_tagged.pk,
            'tagged_content': tagged_content,
            'tagged_file_content': tagged_file_content,    
        }
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'new_file_normal': new_file_message,
        'new_file_tagged': new_file_message,
        'tag_message': new_message
    }
    def connect(self):
        self.room_group_name = 'chat_room'
        
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync( self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
        self.room_group_name, {"type": "chat_message", "message": message}
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))


class GroupChatConsumer(WebsocketConsumer):

    def send_email_in_consumer(self, new_message, sender, content_type, parent_message):
        header_tuple = self.scope.get('headers', [])[0]
        address = header_tuple[1].decode('utf-8')
        ip_address, port = address.split(':')
        domain = f"{ip_address}:{port}"
        
        serialized_message = {
            'id': new_message.id,
            'sender_username': new_message.sender.username,
            'group_name': new_message.group.name,
            'content': new_message.content,
            'timestamp': str(new_message.timestamp),
            'logged_in_user': self.scope['user'].email,
            'has_parent_message': parent_message
            # Add other fields as needed
        }

        get_group_members_emails = new_message.get_group_members_emails

        # Pass only the necessary information to Celery
        task = send_new_group_msg_email_alert_task.apply_async(
                kwargs={
                    'new_message': serialized_message,
                    'sender': sender.username,
                    'domain': domain,
                    'get_group_members_emails': get_group_members_emails,
                    'content_type': content_type
                },
                countdown=15
            )

    def fetch_group_messages(self, data):
        group_messages = get_group_messages(logged_in_user=data['sender'], group_pk=data['groupPk'])
        content = {
            'command': 'group_messages',
            'messages': self.messages_to_json(group_messages)
        }
        self.send_message(content)

    def send_new_group_message(self, data):
        content = {}
        sender = BaseUser.objects.get(username=data['from'])
        group = Group.objects.get(pk=data['groupPk'])
        
        message = data['message']
        message_type = data['type']
        new_message = None
        if message_type == 'normal':
            new_message = GroupChat.objects.create(
                sender = sender,
                content = message,
                group = group
            )
            content = {
                'command': 'new_group_message',
                'message': self.message_to_json(new_message)
            }
            self.send_email_in_consumer(new_message, sender, 'text', 'no')
        elif message_type == 'tagged':
            message_tagged = GroupChat.objects.get(pk=data['parentMessagePk'])
            new_message = GroupChat.objects.create(
                sender=sender,
                content = message,
                group = group,
                message_tagged = message_tagged
            )
            content = {
                'command': 'tagged_new_group_message',
                'message': self.tagged_message_to_json(new_message)
            }
        
            self.send_email_in_consumer(new_message, sender, 'text', 'yes')

        return self.send_chat_message(content)

    def new_file_message(self, data):
        content = {}
        message_type = data['message_type']
        sender = BaseUser.objects.get(username=data['sender'])
        group = Group.objects.get(pk=data['groupPk'])
        message = GroupChat.objects.filter(
                sender=sender, group=group, file_content__isnull=False
                ).order_by('-timestamp').first()
        if message_type == 'normal':
            content = {
            'command': 'new_file_normal',
            'message': self.message_to_json(message)
                }
            self.send_email_in_consumer(message, sender, 'file', 'no')
        elif message_type == 'tagged':
            content = {
                'command': 'new_file_tagged',
                'message': self.tagged_message_to_json(message)
            }
            self.send_email_in_consumer(message, sender, 'file', 'yes')

        return self.send_chat_message(content)
    
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            if message.message_tagged is not None:
                result.append(
                    self.tagged_message_to_json(message)
                )
            elif message.message_tagged is None:
                result.append(
                    self.message_to_json(message)
                )
        return result
    
    def message_to_json(self, message):
        try:
            file_content = message.file_content.url
        except:
            file_content = None

        try:
            content = message.content
        except:
            content = None
        return {
            'sender': message.sender.username,
            'group_name': message.group.name,
            'content': content,
            'file_content': file_content,
            'timestamp': str(message.timestamp),
            'sender_pfp_url': message.sender.pfp.url,
            'pk': message.pk,
        }

    def tagged_message_to_json(self, message):
        try:
            file_content = message.file_content.url
        except:
            file_content = None
        if message.content is not None:
            content = message.content
        else:
            content = None


        try:
            tagged_file_content = message.message_tagged.file_content.url
        except:
            tagged_file_content = None
        try :
            tagged_content = message.message_tagged.content
        except:
            tagged_content = None
        return {
            'sender': message.sender.username,
            'group_name': message.group.name,
            'content': content,
            'timestamp': str(message.timestamp),
            'sender_pfp_url': message.sender.pfp.url,
            'file_content': file_content,
            'pk': message.pk,
            'tagged_pk': message.message_tagged.pk,
            'tagged_content': tagged_content,
            'tagged_file_content': tagged_file_content,
        }

    commands = {
    'fetch_group_messages': fetch_group_messages,
    'new_group_message': send_new_group_message,
    'new_file_normal': new_file_message,
    'new_file_tagged': new_file_message,
    'tag_group_message': send_new_group_message
}
    def connect(self):
        self.room_group_name = 'chat_room'
        
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync( self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
        self.room_group_name, {"type": "chat_message", "message": message}
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))