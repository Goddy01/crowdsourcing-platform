from django.urls import path
from . import views


app_name = 'chat'

urlpatterns = [
    path('', views.room, name='chat'),
    path('<str:room_name>/', views.room, name='room'),
    path('<sender>/set-to-seen/<recipient>', views.set_all_message_to_seen, name='set_to_seen'),
    path('<sender>/send-file/<recipient>', views.send_file_message, name='send_file_msg'),

]