from django.contrib import admin
from .models import Chat, Group, GroupChat

# Register your models here.
admin.site.register(Chat)
admin.site.register(Group)
admin.site.register(GroupChat)
# admin.site.register(TagChat)