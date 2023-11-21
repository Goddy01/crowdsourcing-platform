from django.db.models import Q
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.decorators import login_required
from accounts.models import Connection, Innovator

def index(request):
    user = Innovator.objects.get(user__username=request.user.username)
    friends = Connection.objects.filter(
        Q(user1=user) | Q(user2=user)
    )
    friends = []

    for friend in friends:
        if friend.user1 == user:
            friends.append(friends.user2)
        else:
            friends.append(friends.user1)
    return render(request, 'chat/room.html', {
        'username': mark_safe(json.dumps(request.user.username)),
        'friends': friends,
        'user':user
    })

@login_required
def room(request, room_name):
    user = Innovator.objects.get(user__username=request.user.username)
    friends = Connection.objects.filter(
        Q(user1=user) | Q(user2=user)
    )
    friends = []

    for friend in friends:
        if friend.user1 == user:
            friends.append(friends.user2)
        else:
            friends.append(friends.user1)
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'username': mark_safe(json.dumps(request.user.username)),
        'friends': friends,
        'user':user
    })