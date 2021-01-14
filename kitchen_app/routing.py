from django.urls import path
from . import consumers  
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path('notifications/', consumers.NotificationConsumer().as_asgi()),
    path('ws/chat/<str:room_name>/', ChatConsumer().as_asgi()),
]