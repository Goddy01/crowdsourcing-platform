from django import forms
from chat.models import Chatroom


class ChatRoomForm(forms.ModelForm) : 
    class Meta : 
        model = Chatroom
        fields = "__all__"
        exclude = ["host" ,"participants"]
       
