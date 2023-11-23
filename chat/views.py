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
    qs1 = Chat.objects.filter(sender=sender, recipient=recipient).order_by('timestamp') | Chat.objects.filter(sender=recipient, recipient=sender).order_by('timestamp')
    print('Q1: ', qs1)
    qs2 = Chat.objects.filter(sender=recipient, recipient=sender).order_by('timestamp')
    print('Q2: ', qs2)
    messages = list(chain(qs1, qs2))
    print('M: ', messages)
    return messages