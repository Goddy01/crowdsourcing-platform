from django.db import models
from accounts.models import BaseUser, Innovator
# Create your models here.

def upload_in_chat_files(instance, filename):
    return f'inchat_files/{instance.sender.username} -> {instance.recipient.username}-{filename}'

class Chat(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='chat_sender')
    recipient = models.ForeignKey(BaseUser, on_delete=models.CASCADE, null=True, related_name='chat_recipient')
    content = models.TextField()
    file_content = models.FileField(upload_to=upload_in_chat_files, null=True, blank=True)
    is_seen = models.BooleanField(default=False)

    # class Meta:
    #     ordering = ('-timestamp', )

    def __str__(self):
        return self.sender.username
    
    def last_10_messages():
        return Chat.objects.order_by('timestamp').all()[:10]
    
class Group(models.Model):
    name = models.CharField(max_length=128, unique=True, null=False, blank=False)
    description = models.TextField(max_length=1000)
    members = models.ManyToManyField(BaseUser)

    def __str__(self):
        return self.name
    
    @property
    def members_count(self):
        return self.members.count()
    
class GroupChat(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    content = models.TextField()

    # class Meta:
    #     ordering = ('-timestamp', )

    def __str__(self):
        return self.sender.username
    
    def last_20_messages():
        return GroupChat.objects.order_by('-timestamp').all()[:10]