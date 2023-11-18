from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import BaseUser, Innovator, Moderator, InnovatorSkill, KBAQuestion, ConnectionRequest, Connection
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class AccountAdmin(UserAdmin):
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
class ConnectionRequestAdmin(ImportExportModelAdmin):
    readonly_fields = ('sent_on',)

admin.site.register(BaseUser, AccountAdmin)
admin.site.register(Innovator)
admin.site.register(KBAQuestion)
admin.site.register(Moderator)
admin.site.register(InnovatorSkill)
admin.site.register(ConnectionRequest, ConnectionRequestAdmin)
admin.site.register(Connection)