from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatAgent, ChatRoom, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class ChatAgentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ChatAgent
        fields = ('id', 'user', 'is_available', 'created_at', 'updated_at')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'chat_room', 'sender_type', 'content', 'created_at')

class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    agent = ChatAgentSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ('id', 'customer_email', 'customer_name', 'agent', 'status', 
                 'created_at', 'updated_at', 'messages')