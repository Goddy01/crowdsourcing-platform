from django.shortcuts import render
import os
import time
import json
from chat.agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Publisher
from pusher import Pusher

# Create your views here.
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q , Count
from django.contrib import messages 
from django.contrib.auth.decorators import login_required 
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models.signals import post_save

from chat.forms import ChatRoomForm
from chat.models import Topic , Message , Chatroom, Messages, Todos
from accounts.models import BaseUser
from django.views.decorators.csrf import csrf_exempt


# Importing the User Models
from django.contrib.auth import get_user_model
User = get_user_model()


@login_required
def chat(request):
    if request.user.is_authenticated:
        q = request.GET.get("q").strip() if request.GET.get("q") != None else ""
        rooms = Chatroom.objects.filter(
            Q(topic__name__icontains=q) |
            Q(roomname__icontains=q) |
            Q(description__icontains=q)
        )
        rooms_count = rooms.count()
        rooms = rooms[:6]
        topics = Topic.objects.all()
        topics_count = topics.count()
        topics = topics[:5]
        room_messages = Message.objects.filter(
            Q(room__topic__name__icontains = q)
        )[:5]

        todos = Todos.objects.all()
        

        user = request.user
        messages = Messages.get_message(user=request.user)
        active_direct = None
        directs = None
        profile = get_object_or_404(BaseUser, pk=user.pk)

        all_users = User.objects.all()

        if messages:
            message = messages[0]
            active_direct = message['user'].username
            directs = Messages.objects.filter(user=request.user, reciepient=message['user'])
            directs.update(is_read=True)

            for message in messages:
                if message['user'].username == active_direct:
                    message['unread'] = 0

        context = {

            "todos": todos, 
            "all_users": all_users, 
            "rooms": rooms, 
            "topics": topics, 
            "room_messages" : room_messages , 
            "rooms_count": rooms_count , 
            "topics_count" : topics_count,
            'directs':directs,
            'messages': messages,
            'active_direct': active_direct,
            'profile': profile,
            
            }
        return render(request, "chat/chat-home.html", context)



@login_required
def leaveRoom(request, pk):
    room = Chatroom.objects.get(id=pk)
    profile = BaseUser.objects.get(pk=request.user.pk)

    if request.user.is_authenticated:
        room.participants.remove(request.user)
        profile.rooms.remove(room)

        messages.success(request, f'You left {room.roomname} successfully.')
        return redirect("chats:chat-room", room.pk)
    else:
        messages.warning(request, f'You need to login before you can join any room.')
        return redirect("accounts:innovator_login")


@login_required
def deleteMessage(request, pk):
    messages = Messages.objects.get(id=pk)
    messages.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def Room(request, pk):
    user = request.user 
    room = Chatroom.objects.get(id = pk)
    if not room : 
        return redirect("chats:message")
    room_messages = room.message_set.all()[:20]
    
    all_users = User.objects.all()

    # all Rooms
    q = request.GET.get("q").strip() if request.GET.get("q") != None else ""
    rooms = Chatroom.objects.filter(
        Q(topic__name__icontains=q) |
        Q(roomname__icontains=q) |
        Q(description__icontains=q)
    )
    rooms_count = rooms.count()
    rooms = rooms[:6]
    topics = Topic.objects.all()
    topics_count = topics.count()
    topics = topics[:5]

    context = {
        "room": room ,
        "room_messages" : room_messages ,
        "user" : user,
        "all_users" : all_users,
        "rooms": rooms, 
        "topics": topics, 
        "rooms_count": rooms_count , 
        "topics_count" : topics_count
    
    } 
    return render(request, "chat/chat-room.html", context)



@login_required
def JoinRoom(request , pk) : 
    profile = BaseUser.objects.get(pk=request.user.pk)
    room = Chatroom.objects.get(id = pk)

    if not room : 
        return redirect("chats:message")

    if request.user.is_authenticated : 
        room.participants.add(request.user)
        # profile.rooms.add(room)
        messages.success(request, f'You have joined {room.roomname}.')
    else : 
        messages.warning(request , "You have to Login first in order to join a room !") 

    return redirect("chats:chat-room" , pk=pk)



@login_required
def CreateRoom(request):
    topics = Topic.objects.all()
    if request.method == "POST":
        form = ChatRoomForm(request.POST, request.FILES)
        topic_name = request.POST.get("topic")
        topic , created = Topic.objects.get_or_create(name = topic_name )
        
        new_room = Chatroom.objects.create(
            host=request.user , 
            roomname = request.POST.get("roomname") , 
            topic = topic , 
            description = request.POST.get("description" ),
            image = request.FILES.get("image" )
        )
        new_room.participants.add(request.user.pk)
        
        return redirect("chats:chat-room" , pk=new_room.id)
    else:
        form = ChatRoomForm()
    context = {"form": form, "button_value": "Create" , "topics" : topics}
    return render(request, "chat/room_form.html", context)

@login_required 
def UpdateRoom(request, pk):
    room = Chatroom.objects.get(id=pk)
    if not room : 
        return redirect("chats:message")
    form = ChatRoomForm(instance = room)
    if request.user != room.host :
        messages.error(request , "You are not allowed to Edit Room Settings !") 
        return redirect("chats:message")

    if request.method == "POST":
        room.roomname = request.POST.get("roomname")
        room.topic , created = Topic.objects.get_or_create(name = request.POST.get("topic"))
        room.description = request.POST.get("description")

        room.save()
        return redirect("chats:chat-room" , pk=room.id)
    context = {"form": form, "button_value": "Update"  , "room" : room }
    return render(request, "chat/room_update_form.html", context)


def SendMSG(request, pk):
    
    if request.method == "POST":
        user = request.user
        room = Chatroom.objects.get(id=pk)

        body = request.POST.get("body")
        new_chat = Message.objects.create(user=user, room=room, body=body)
        
        # return redirect('message')
        success = "Message Sent."
        return HttpResponse(success)


@login_required
def Directs(request, username):
    user  = request.user
    messages = Messages.get_message(user=user)
    active_direct = username
    directs = Messages.objects.filter(user=user, reciepient__username=username)  
    directs.update(is_read=True)


    q = request.GET.get("q").strip() if request.GET.get("q") != None else ""
    rooms = Chatroom.objects.filter(
        Q(topic__name__icontains=q) |
        Q(roomname__icontains=q) |
        Q(description__icontains=q)
    )
    rooms_count = rooms.count()
    rooms = rooms[:6]
    topics = Topic.objects.all()
    topics_count = topics.count()
    topics = topics[:5]
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains = q)
    )[:5]

    all_users = User.objects.all()


    for message in messages:
            if message['user'].username == username:
                message['unread'] = 0
    context = {
        'all_users': all_users,
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
        "room_messages" : room_messages ,
        "user" : user,
        "rooms": rooms, 
        "topics": topics, 
        "rooms_count": rooms_count , 
        "topics_count" : topics_count
    }
    return render(request, 'chat/chat-home.html', context)

@csrf_exempt
def SendDirect(request):
    if request.method == "POST":
        from_user = request.user
        to_user_username = request.POST.get('to_user')
        body = request.POST.get('body')
        file = request.FILES.get('file_field')
        print('FILE RE', file)

        # to_user = User.objects.get(username=to_user_username)
        m = Messages(user=get_object_or_404(BaseUser, username=from_user.username), sender=get_object_or_404(BaseUser, username=from_user.username), reciepient=get_object_or_404(BaseUser, username=to_user_username), body=body, file=file)
        m.save()
        # return redirect('message')
        success = "Message Sent."
        return HttpResponse(success)

def UserSearch(request):
    query = request.GET.get('q')
    # profile = Profile.objects.all()

    context = {}
    if query:
        users = User.objects.filter(Q(username__icontains=query))
        profiles = BaseUser.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(middle_name__icontains=query))

        # Paginator
        # paginator = Paginator(users, 8)
        # page_number = request.GET.get('page')
        # users_paginator = paginator.get_page(page_number)

        context = {
            'users': users,
            'profiles': profiles,
            'query':query,
            }

    return render(request, 'chat/search.html', context)

def NewConversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('search-users')
    if from_user != to_user:
        Messages.sender_message(from_user, to_user, body)
    return redirect('message')

@csrf_exempt
def TodoDelete(request):
    if request.method == "POST":
        id = request.POST.get("cid")
        todo = Todos.objects.get(pk=id)
        todo.delete()
        return JsonResponse({"status":1})
    else:
        return JsonResponse({"status": 0})


def CreateTodo(request):
    if request.method == "POST":
        todo = request.POST.get("todo")
        user = request.user

        new_todo = Todos.objects.create(user=user, todo=todo)
        new_todo.save()
        success = "Todo Added"
        return HttpResponse(success)
    

# Instantiate a Pusher Client
pusher_client = Pusher(app_id=os.environ.get('PUSHER_APP_ID'),
                       key=os.environ.get('PUSHER_KEY'),
                       secret=os.environ.get('PUSHER_SECRET'),
                 
                       cluster=os.environ.get('PUSHER_CLUSTER')
                       )


@login_required
def index(request, active_direct):
    User = BaseUser
    all_users = User.objects.exclude(id=request.user.id).only('id', 'username')
    pusher_id = os.environ.get('PUSHER_APP_ID')
    return render(request, 'chat/index.html', {'allUsers': all_users, 'active_direct': active_direct, 'pusher_id': pusher_id})


def pusher_auth(request):
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'],
        custom_data={
            'user_id': request.user.id,
            'user_info': {
                'id': request.user.id,
                'name': request.user.username
            }
        })
    return JsonResponse(payload)


def generate_agora_token(request):
    appID = os.environ.get('AGORA_APP_ID')
    appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')
    channelName = json.loads(request.body.decode(
        'utf-8'))['channelName']
    userAccount = request.user.username
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, Role_Publisher, privilegeExpiredTs)

    return JsonResponse({'token': token, 'appID': appID})


def call_user(request):
    body = json.loads(request.body.decode('utf-8'))

    user_to_call = body['user_to_call']
    channel_name = body['channel_name']
    caller = request.user.pk

    pusher_client.trigger(
        'presence-online-channel',
        'make-agora-call',
        {
            'userToCall': user_to_call,
            'channelName': channel_name,
            'from': caller
        }
    )
    return JsonResponse({'message': 'call has been placed'})