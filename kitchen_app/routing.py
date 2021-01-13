from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from . import consumers  # Importing notification Consumer from consumers.py

websocket_urlpatterns = [
    path('notifications/', consumers.NotificationConsumer()),
]