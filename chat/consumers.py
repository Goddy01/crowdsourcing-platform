import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .models import Chat, GroupChat
from accounts.models import BaseUser
from django.db.models import Q


class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        sender = data.get('sender')
        sender_user =BaseUser.objects.get(username=sender)
        recipient = data.get('recipient_username')
        recipient_user = BaseUser.objects.get(username=recipient)
        print('RECIPIENT USERNAME: ', recipient)
        messages = Chat.last_10_messages()
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        sender = data['from']
        recipient = data['to']
        sender_user = BaseUser.objects.get(username=sender)
        recipient_user = BaseUser.objects.get(username=recipient)
        message = Chat.objects.create(
            sender=sender_user,
            recipient=recipient_user,
            content=data['message']
        )

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(
                self.message_to_json(message)
            )
        return result
    def message_to_json(self, message):
        return {
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'content': message.content,
            'timestamp': str(message.timestamp),
            'sender_pfp_url': message.sender.pfp.url

        }
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        print('ROOM NAME: ', self.room_name)
        self.room_group_name = f"chat_{self.room_name}"
        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync( self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        # message = data["message"]
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
        self.room_group_name, {"type": "chat.message", "message": message}
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))
    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))