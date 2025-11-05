from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from .models import ChatAgent, ChatRoom, Message
from .serializers import ChatAgentSerializer, ChatRoomSerializer, MessageSerializer
from django.db.models import Q

class ChatAgentViewSet(viewsets.ModelViewSet):
    queryset = ChatAgent.objects.all()
    serializer_class = ChatAgentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def my_chats(self, request):
        agent = ChatAgent.objects.get(user=request.user)
        chats = ChatRoom.objects.filter(agent=agent)
        serializer = ChatRoomSerializer(chats, many=True)
        return Response(serializer.data)

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

    @action(detail=True, methods=['post'])
    def assign_agent(self, request, pk=None):
        chat_room = self.get_object()
        agent_id = request.data.get('agent_id')
        
        try:
            agent = ChatAgent.objects.get(id=agent_id, is_available=True)
            chat_room.agent = agent
            chat_room.status = 'assigned'
            chat_room.save()
            return Response({'status': 'agent assigned'})
        except ChatAgent.DoesNotExist:
            return Response(
                {'error': 'Agent not found or not available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@xframe_options_exempt
def chat_widget(request):
    return render(request, 'chat/widget.html')

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

def chat_widget(request):
    return render(request, 'chat/widget.html')
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.request.query_params.get('chat_room', None)
        if chat_room_id:
            return Message.objects.filter(chat_room_id=chat_room_id)
        return Message.objects.none()

def chat_agent_portal(request):
    return render(request, 'chat/agent_portal.html')

def customer_chat(request):
    """Customer chat interface"""
    return render(request, 'chat/customer_chat.html')

def chat_widget(request):
    """Embedded chat widget view"""
    return render(request, 'chat/widget.html')