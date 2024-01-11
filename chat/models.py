from django.db import models
from accounts.models import BaseUser, Innovator
from core.models import Project, Make_Investment
# Create your models here.

def upload_in_chat_files(instance, filename):
    return f'inchat_files/{instance.sender.username} -> {instance.recipient.username}-{filename}'

def upload_group_inchat_files(instance, filename):
    return f'group_inchat_files/{instance.sender.username} -> {instance.group.name}-{filename}'

# class ChatManager(models.Manager):
#     def by_sender_recipient(self, sender, recipient):
#         qs = (Chat.objects
#               .filter(sender__username=sender, recipient__username=recipient) |
#               Chat.objects.filter(sender__username=recipient, recipient__username=sender)
#               .order_by('timestamp'))

#         # new_qs = []
#         # for queryset in qs:
#         #     new_qs.append(queryset)

#         return qs

class Chat(models.Model):
    message_tagged = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply_to')
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='chat_sender')
    recipient = models.ForeignKey(BaseUser, on_delete=models.CASCADE, null=True, related_name='chat_recipient')
    content = models.TextField()
    file_content = models.FileField(upload_to=upload_in_chat_files, null=True, blank=True)
    # is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp', )
    # objects = ChatManager()

    # def __str__(self):
    #     return f'{self.sender.username} -- {self.recipient.username}'
    
    def last_10_messages():
        return Chat.objects.order_by('timestamp').all()[:10]
    

# class TagChat(models.Model):
#     message_tagged = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name='message_tagged')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     sender = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='t_chat_sender')
#     recipient = models.ForeignKey(BaseUser, on_delete=models.CASCADE, null=True, related_name='t_chat_recipient')
#     content = models.TextField()
#     file_content = models.FileField(upload_to=upload_in_chat_files, null=True, blank=True)
    
class Group(models.Model):
    name = models.CharField(max_length=128, unique=True, null=False, blank=False)
    description = models.TextField(max_length=1000)
    members = models.ManyToManyField(BaseUser)
    investment_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=False)

    def __str__(self):
        return self.name
    
    @property
    def members_count(self):
        return self.members.count()
    
    @property
    def get_group_members(self):
        project_owner = self.investment_project.innovator.user
        members = []
        for member in self.members.all():
            if member != project_owner:
                members.append(member)
            if Make_Investment.objects.filter(sender__user=project_owner).exists():
                members.append(project_owner)
        return members
    
class GroupChat(models.Model):
    message_tagged = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply_to')
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    content = models.TextField()
    file_content = models.FileField(upload_to=upload_group_inchat_files, null=True, blank=True)

    class Meta:
        ordering = ('timestamp', )

    # def __str__(self):
    #     return self.sender.username
    
    def last_20_messages():
        return GroupChat.objects.order_by('-timestamp').all()[:10]
    
    @property
    def get_group_members_emails(self):
        member_emails = []
        members = self.group.members.all()
        for member in members:
            if member.receive_msg_email_notif and member != self.sender:
                member_emails.append(member.email)
        return member_emails