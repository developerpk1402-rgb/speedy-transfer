import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message, ChatAgent
from .ai_handler import ChatAIHandler

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            print("WebSocket connection attempt received")
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            self.ai_handler = ChatAIHandler()

            print(f"Attempting to join room: {self.room_group_name}")
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            print("Accepting connection")
            await self.accept()
            print("Connection accepted")

            # Send welcome message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': '¡Hola! Soy el asistente virtual de Speedy Transfer. ¿En qué puedo ayudarte hoy?',
                    'sender_type': 'ai',
                    'timestamp': timezone.now().isoformat()
                }
            )
            print("Welcome message sent")
        except Exception as e:
            print(f"Error in connect: {str(e)}")
            raise

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_type = text_data_json.get('sender_type', 'customer')

        # Save customer message to database
        await self.save_message(message, sender_type)

        # Send customer message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_type': sender_type,
                'timestamp': timezone.now().isoformat()
            }
        )

        # Generate and send AI response if no agent is assigned
        if sender_type == 'customer':
            chat_room = await self.get_chat_room()
            if not chat_room.agent:
                # Get conversation history for context
                history = await self.get_chat_history()
                # Get AI response
                ai_response = await self.ai_handler.get_ai_response(message, history)
                # Save AI response to database
                await self.save_message(ai_response, 'ai')
                # Send AI response to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': ai_response,
                        'sender_type': 'ai',
                        'timestamp': timezone.now().isoformat()
                    }
                )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_type': event['sender_type'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, message, sender_type):
        chat_room = ChatRoom.objects.get(id=int(self.room_name))
        Message.objects.create(
            chat_room=chat_room,
            content=message,
            sender_type=sender_type
        )
    
    @database_sync_to_async
    def get_chat_room(self):
        return ChatRoom.objects.get(id=int(self.room_name))

    @database_sync_to_async
    def get_chat_history(self):
        """Get the last few messages from the chat history for context"""
        chat_room = ChatRoom.objects.get(id=int(self.room_name))
        messages = Message.objects.filter(chat_room=chat_room).order_by('-created_at')[:5]
        
        # Convert to format suitable for OpenAI API
        history = []
        for msg in reversed(messages):
            role = "assistant" if msg.sender_type == "ai" else "user"
            history.append({
                "role": role,
                "content": msg.content
            })
            
        return history