from django.db import models
from accounts.models import BaseUser
# Create your models here.


class Message(models.Model):
    body = models.TextField()
    sent_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(BaseUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.sent_by}"