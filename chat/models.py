from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class ChatAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agent: {self.user.email}"

class ChatRoom(models.Model):
    CHAT_STATUS = (
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('closed', 'Closed'),
    )

    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)
    agent = models.ForeignKey(ChatAgent, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=CHAT_STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat with {self.customer_name}"

class Message(models.Model):
    MESSAGE_TYPES = (
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('ai', 'AI'),
    )

    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender_type} message in {self.chat_room}"