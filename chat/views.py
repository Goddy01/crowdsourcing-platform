from django.db.models import Q
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.decorators import login_required
from accounts.models import Connection, Innovator

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