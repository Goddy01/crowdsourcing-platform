from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class AccountAdmin(UserAdmin):
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    list_filter = ()
admin.site.register(User, AccountAdmin)