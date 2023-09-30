from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from chat.models import Todos, Topic , Message , Chatroom, Messages



class TopicAdmin(ImportExportModelAdmin):
    pass

class MessageAdmin(ImportExportModelAdmin):
    pass

class ChatroomAdmin(ImportExportModelAdmin):
    pass

class MessagesAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Topic, TopicAdmin)
admin.site.register(Todos)
admin.site.register(Message, MessageAdmin)
admin.site.register(Chatroom, ChatroomAdmin)
admin.site.register(Messages, MessagesAdmin)
