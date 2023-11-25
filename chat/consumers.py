import json
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .models import Chat, GroupChat
from accounts.models import BaseUser
from .views import get_messages


class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        sender = BaseUser.objects.get(username=data.get('sender'))
        recipient = BaseUser.objects.get(username=data.get('recipient'))
        # messages = Chat.last_10_messages()
        logged_in_user = BaseUser.objects.get(username=self.scope['user'].username)
        messages = get_messages(sender=sender, recipient=recipient)
        for message in messages:
            if logged_in_user == message.recipient:
                message.is_seen = True
                message.save(update_fields=['is_seen'])
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        sender = data['from']
        sender_user = BaseUser.objects.get(username=sender)
        print('TO: ', data['to'])
        message = Chat.objects.create(
            sender=sender_user,
            recipient=BaseUser.objects.get(username=data['to']),
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
            if message.recipient == BaseUser.objects.get(username=self.scope['user'].username):
                message.is_seen = True
                message.save(update_fields =['is_seen'])
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
            'sender_pfp_url': message.sender.pfp.url,
            'is_seen': message.is_seen

        }
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }
    def connect(self):
        # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_room"
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