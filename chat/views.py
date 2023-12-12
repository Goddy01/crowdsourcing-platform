from django.http import JsonResponse
from accounts.models import BaseUser
from itertools import chain
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.decorators import login_required
from accounts.models import Connection, Innovator
from .models import Chat, Group, GroupChat
from django.core.serializers import serialize

def index(request):
    return render(request, 'chat/chat.html')

@login_required
def room(request, room_name=None):
    if room_name is not None:
        room_name = mark_safe(json.dumps(room_name))
    user = Innovator.objects.get(user__username=request.user.username)
    friends_list = Connection.objects.filter(
        Q(user1=user) | Q(user2=user)
    )
    conversations = []

    # for friend in friends_list:
    #     if friend.user1 == user:
    #         conversations.append(friend.user2)
    #     else:
    #         conversations.append(friend.user1)
    return render(request, 'chat/room.html', {
        'username': request.user.username,
        'room_name_json': room_name,
        'friends': conversations,
        'friends_list': friends_list,
        'groups': Group.objects.filter(members=user.user.pk),
        'groups2': serialize('json', queryset=Group.objects.filter(members=user.user.pk)),
        'user':user
    })


def get_messages(sender, recipient):
    qs1 = Chat.objects.filter(sender__username=sender, recipient__username=recipient)
    qs2 = Chat.objects.filter(sender__username=recipient, recipient__username=sender)

    return qs1 | qs2

def get_group_messages(logged_in_user, group_pk):
    group = get_object_or_404(Group, group_pk)
    if logged_in_user in group.members:
        return GroupChat.objects.filter(group=group)

# def set_all_message_to_seen(request, sender, recipient):
#     messages = Chat.objects.filter(
#         sender__username=sender,
#         recipient__username=recipient,
#         is_seen=False
#     )
#     for m in messages:
#         m.is_seen = True
#         m.save(update_fields=['is_seen'])
#     print('SHITE')
#     return JsonResponse(data = {'status': 'success'})

# @login_required

def get_group_members(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    
    # Select specific fields for each member
    members = group.members.all().values('first_name', 'last_name', 'middle_name', 'pfp', 'username')

    return JsonResponse({'members': list(members)})

def send_file_message(request, sender, recipient, parent_message=None):
    if request.method == "POST" and request.FILES.get("file"):
        print('R* : ', recipient)
        tagged_file_content = None
        sender = BaseUser.objects.get(username=sender)
        recipient = BaseUser.objects.get(username=recipient)
        file = request.FILES['file']
        if parent_message is None:
            message  = Chat.objects.create(
                sender=sender,
                recipient=recipient,
                file_content=file
            )
            print('FILE CREATED')
        if parent_message is not None:
            print('Parent Message: ', parent_message)
            messages_tagged = Chat.objects.get(pk=parent_message)
            
            message  = Chat.objects.create(
                sender=sender,
                recipient=recipient,
                file_content=file,
                message_tagged = messages_tagged
            )
            print('TAGGED FILE CREATED')
    return JsonResponse(data = 
        {
        'status': 'success', 
        'file_url': message.file_content.url, 
        'message_sender': message.sender.username, 
        'message_sender_pfp_url': message.sender.pfp.url, 
        'message_recipient': message.recipient.username, 
        'message_recipient_url': message.recipient.pfp.url, 
        'timestamp': message.timestamp
        })