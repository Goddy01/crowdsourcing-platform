from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/friends/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/chat/groups/$", consumers.GroupChatConsumer.as_asgi()),
]