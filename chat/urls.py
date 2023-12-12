from django.urls import path
from . import views


app_name = 'chat'

urlpatterns = [
    # path('<room_name>/', views.room, name='chat'),
    path('', views.room, name='chat'),
    path('<sender>/send-file/<recipient>/', views.send_file_message, name='send_file_msg'),
    path('<parent_message>/<sender>/send-file/<recipient>/', views.send_file_message, name='send_file_msg_with_parent'),

    path('<group_pk>/<sender>/send-file', views.send_group_file_message, name='send_group_file_msg'),
    path('<group_pk>/<parent_message>/<sender>/send-file', views.send_group_file_message, name='send_group_file_msg_with_parent'),
    path('<group_pk>/get-group-members', views.get_group_members, name='get_group_members'),

]