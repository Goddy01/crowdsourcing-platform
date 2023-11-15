from django.db import models
from accounts.models import BaseUser
# Create your models here.

class Chat(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        if self.content:
            return f"{self.content[:15]}"
        return self.sender.username
    
class Group(models.Model):
    name = models.CharField(max_length=128, unique=True, null=False, blank=False)
    description = models.TextField(max_length=1000)
    members = models.ManyToManyField(BaseUser)

    def __str__(self):
        return self.name