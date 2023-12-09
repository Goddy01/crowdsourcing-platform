import json
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer, SyncConsumer
from .models import Chat, GroupChat, Group
from accounts.models import BaseUser
from .views import get_messages
from django.shortcuts import get_object_or_404


class ChatConsumer(WebsocketConsumer):
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
        if data['message_type'] == 'normal':
            message = Chat.objects.filter(sender=sender, recipient=recipient, file_content__isnull=False).order_by('-timestamp').first()
            content = {
            'command': 'new_file_normal',
            'message': self.tag_message_to_json(message)
                }

        elif data['message_type'] == 'tagged':
            message = Chat.objects.filter(sender=sender, recipient=recipient, file_content__isnull=False).order_by('-timestamp').first()
            content = {
                'command': 'new_file_tagged',
                'message': self.tag_message_to_json(message)
            }
        return self.send_chat_message(content)

    def new_message(self, data):
        content = {}
        sender = data['from']
        sender_user = BaseUser.objects.get(username=sender)
        recipient = BaseUser.objects.get(username=data['to'])
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
            print('MESSAGE TAGGED: ', parent_message)
            message_tagged = Chat.objects.get(pk=parent_message)
            message = Chat.objects.create(
                message_tagged = message_tagged,
                sender = sender_user,
                recipient = recipient,
                content = message
            )
            content = {
                'command': 'tag_message',
                'message': self.tag_message_to_json(message)
            }
            
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
                    self.tag_message_to_json(message)
                )
            else:
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
    
    def tag_message_to_json(self, message):
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
        if message.message_tagged.content is not None:
            tagged_content = message.message_tagged.content
        else:
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
            'tagged_file_content': tagged_file_content

        }
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'new_file_normal': new_file_message,
        'new_file_tagged': new_file_message,
        'tag_message': new_message
    }
    def connect(self):
        print('6')
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
        print('10')
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))


# class GroupChatConsumer(WebsocketConsumer):
#     def fetch_group_messages(self, data):
#         sender = get_object_or_404(BaseUser, username=data['sender'])
#         group = Group.objects.get(Group, pk=data['groupPk'])
#         logged_in_user = get_object_or_404(BaseUser, username=self.scope['user'].username)