from distutils.command.upload import upload
from django.db import models

from email.policy import default
from django.db import models
from PIL import Image
from django.db.models import Max
from django.forms import DateTimeField
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


User = settings.AUTH_USER_MODEL
UserModel = get_user_model()

class Topic(models.Model) : 
    name = models.CharField(max_length = 100) 
    created = models.DateTimeField(auto_now_add = True)
    class Meta : 
        ordering = ["created"]
    
    def __str__(self): 
        return str(self.name)


class Chatroom(models.Model) : 
    image = models.ImageField(default="default-room.jpg", upload_to="room_thumbnails")
    host = models.ForeignKey(User , on_delete = models.CASCADE ) 
    topic = models.ForeignKey("chat.Topic", verbose_name="topic", on_delete=models.SET_NULL , null = True, related_name="chatroom_topic")
    roomname = models.CharField(max_length = 200 )
    description = models.TextField(null = True ,  blank = True)
    participants = models.ManyToManyField(User, verbose_name="participants" , related_name = "participants"  )
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)
    
    class Meta : 
        ordering = ["-updated" , "-created"]
    
    def __str__(self) : 
        return str(self.roomname)  + " created by -> " + str(self.host) + " on " + str(self.topic) 
    
class Message(models.Model) : 
    user = models.ForeignKey(User , on_delete = models.CASCADE) 
    room = models.ForeignKey(Chatroom , on_delete = models.CASCADE) 
    body = models.TextField()
    udpated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True) 
    
    class Meta: 
        ordering = ["udpated" , "created"]
    
    def __str__(self) : 
        return str(self.user) + "texted ->" + str(self.body)[:50]


def files_location(instance, filename):
    return f'chat-files/{instance.sender.username}-{instance.reciepient.username}/{instance.pk}/-{filename}'

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    reciepient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    file = models.FileField(upload_to=files_location, null=True, blank=True)
    body = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def sender_message(from_user, to_user, body, file):
        sender_message = Messages(
            user=from_user,
            sender = from_user,
            reciepient = to_user,
            body = body,
            file = file,
            is_read = True
            )
        sender_message.save()
    
        reciepient_message = Messages(
            user=to_user,
            sender = from_user,
            reciepient = from_user,
            body = body,
            file = file,
            is_read = True
            )
        reciepient_message.save()
        return sender_message

    def get_message(user):
        users = []
        messages = Messages.objects.filter(user=user).values('reciepient').annotate(last=Max('date')).order_by('-last')
        for message in messages:
            users.append({
                'user': UserModel.objects.get(pk=message['reciepient']),
                'last': message['last'],
                'unread': Messages.objects.filter(user=user, reciepient__pk=message['reciepient'], is_read=False).count()
            })
        return users


class Todos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo = models.CharField(max_length=1000)
    completed = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.todo[:20]