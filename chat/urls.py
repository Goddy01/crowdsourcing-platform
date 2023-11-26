from django.urls import path
from . import views


app_name = 'chat'

urlpatterns = [
    path('', views.room, name='chat'),
    path('<str:room_name>/', views.room, name='room'),
    path('set-to-seen', views.set_all_message_to_seen, name='set_to_seen')
]