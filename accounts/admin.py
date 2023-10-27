from django.contrib import admin
from .models import BaseUser, Innovator, Moderator, InnovatorSkill, KBAQuestion
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class AccountAdmin(UserAdmin):
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(BaseUser, AccountAdmin)

# class InnovatorAdmin(UserAdmin):
#     readonly_fields = ('date_joined', 'last_login')
#     filter_horizontal = ()
#     list_filter = ()
#     fieldsets = ()
admin.site.register(Innovator)
admin.site.register(KBAQuestion)
admin.site.register(Moderator)
admin.site.register(InnovatorSkill)