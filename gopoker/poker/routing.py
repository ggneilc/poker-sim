from django.urls import path
from .consumers import *

websocket_urlpatterns = [
  path("ws/room/<room_id>", PokerroomConsumer.as_asgi()),
]