import json
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, GroupChat, Group
from accounts.models import BaseUser
from .views import get_messages
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def fetch_messages(self, data):
        print('1')
        sender = BaseUser.objects.get(username=data['sender'])
        recipient = BaseUser.objects.get(username=data.get('recipient'))
        logged_in_user = BaseUser.objects.get(username=self.scope['user'].username)
        messages = get_messages(sender=sender, recipient=recipient)
        for message in messages:
            if logged_in_user == message.recipient:
                message.is_seen = True
                message.save(update_fields=['is_seen'])
        content = {
            'command': 'messages',
            'messages': await self.messages_to_json(messages)
        }
        await self.send_message(content)

    async def new_file_message(self, data):
        print('2')
        sender = BaseUser.objects.get(username=data['sender'])
        recipient = BaseUser.objects.get(username=data['recipient'])
        message = Chat.objects.filter(sender=sender, recipient=recipient, file_content__isnull=False).order_by('-timestamp').first()

        content = {
            'command': 'new_file',
            'message': await self.message_to_json(message)
        }

        await self.send_chat_message(content)

    async def new_message(self, data):
        print('3')
        sender = data['from']
        sender_user = BaseUser.objects.get(username=sender)

        message = await Chat.objects.create(
            sender=sender_user,
            recipient=BaseUser.objects.get(username=data['to']),
            content=data['message']
        )

        content = {
            'command': 'new_message',
            'message': await self.message_to_json(message)
        }
        await self.send_chat_message(content)

    async def messages_to_json(self, messages):
        result = []
        for message in messages:
            if message.recipient == BaseUser.objects.get(username=self.scope['user'].username):
                message.is_seen = True
                message.save(update_fields=['is_seen'])
            result.append(
                await self.message_to_json(message)
            )
        return result

    async def message_to_json(self, message):
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
            'is_seen': message.is_seen,
            'file_content': file_content,
            'pk': message.pk,
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'new_file': new_file_message
    }

    async def connect(self):
        print('6')
        self.room_group_name = "chat_room"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print('7')
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print('8')
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)

    async def send_chat_message(self, message):
        print('9')
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    async def send_message(self, message):
        print('10')
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event):
        chat_list = []
        message = event["message"]
        print('Message: ', message)
        self.send(text_data=json.dumps(message))
        # chat_list.append(message['pk'])
