from django.urls import path
from . import views


app_name = 'chat'

urlpatterns = [
    path('', views.room, name='chat'),
    path('<sender>/send-file/<recipient>', views.send_file_message, name='send_file_msg'),
    path('<group_pk>/get-group-members', views.get_group_members, name='get_group_members'),

]