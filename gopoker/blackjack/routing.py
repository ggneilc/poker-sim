from django.urls import path
from .consumers import BlackjackConsumer

websocket_urlpatterns = [
  path("ws/blackjack/<room_id>", BlackjackConsumer.as_asgi()),
]
