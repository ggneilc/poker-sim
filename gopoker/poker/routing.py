from django.urls import path
from .consumers import *

websocket_urlpatterns = [
  path("ws/room/<pokerroom_name>", PokerroomConsumer.as_asgi()),
]