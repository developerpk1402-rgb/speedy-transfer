from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'agents', views.ChatAgentViewSet)
router.register(r'rooms', views.ChatRoomViewSet)
router.register(r'messages', views.MessageViewSet)

app_name = 'chat'

urlpatterns = [
    path('api/', include(router.urls)),
    path('agent-portal/', views.chat_agent_portal, name='agent_portal'),
    path('customer/', views.customer_chat, name='customer_chat'),
    path('widget/', views.chat_widget, name='chat_widget'),
]