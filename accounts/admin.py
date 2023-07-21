from django.contrib import admin
from .models import BaseUser, Contributor
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class AccountAdmin(UserAdmin):
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(BaseUser, AccountAdmin)

# class ContributorAdmin(UserAdmin):
#     readonly_fields = ('date_joined', 'last_login')
#     filter_horizontal = ()
#     list_filter = ()
#     fieldsets = ()
admin.site.register(Contributor)