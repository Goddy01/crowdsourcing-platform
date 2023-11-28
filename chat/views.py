from django.http import JsonResponse
from accounts.models import BaseUser
from itertools import chain
from django.db.models import Q
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.decorators import login_required
from accounts.models import Connection, Innovator
from .models import Chat

def index(request):
    return render(request, 'chat/chat.html')

@login_required
def room(request):
    user = Innovator.objects.get(user__username=request.user.username)
    friends_list = Connection.objects.filter(
        Q(user1=user) | Q(user2=user)
    )
    friends = []

    for friend in friends_list:
        if friend.user1 == user:
            friends.append(friend.user2)
        else:
            friends.append(friend.user1)
    return render(request, 'chat/room.html', {
        'username': request.user.username,
        'friends': friends,
        'user':user
    })

def get_messages(sender, recipient):
    qs1 = Chat.objects.filter(sender=sender, recipient=recipient).order_by('timestamp')
    qs2 = Chat.objects.filter(sender=recipient, recipient=sender).order_by('timestamp')

    return qs1 | qs2

def set_all_message_to_seen(request, sender, recipient):
    messages = Chat.objects.filter(
        sender__username=sender,
        recipient__username=recipient,
        is_seen=False
    )
    for m in messages:
        m.is_seen = True
        m.save(update_fields=['is_seen'])
    print('SHITE')
    return JsonResponse(data = {'status': 'success'})

@login_required
def send_file_message(request, sender, recipient):
    if request.method == 'POST':
        sender = BaseUser.objects.get(username=sender)
        recipient = BaseUser.objects.get(username=recipient)
        file = request.FILES['file']
        message  = Chat.objects.create(
            sender=sender,
            recipient=recipient,
            content='',
            file_content=file
        )
    return JsonResponse(data = {'status': 'success', 'file_url': message.file_content.url})