from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from .models import *
from poker.utils import *
import json

class PokerroomConsumer(WebsocketConsumer):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.event_handlers = {
      'chat_message': self.handle_chat_message,
      'player_joined': self.player_joined,
      'start_game': self.handle_start_game
    }

  def connect(self):
    self.user = self.scope['user']
    self.pokerroom_name = self.scope['url_route']['kwargs']['room_id']
    self.pokerroom = get_object_or_404(PokerRoom, link=self.pokerroom_name)

    async_to_sync(self.channel_layer.group_add)(
      self.pokerroom_name, self.channel_name
    )
    self.accept()

    self.handle_broadcast_message("has joined")

  def disconnect(self, code):
    async_to_sync(self.channel_layer.group_discard)(
      self.pokerroom_name, self.channel_name
    )

    self.handle_broadcast_message("has left")

  def receive(self, text_data):
    data = json.loads(text_data)
    event_type = data.get('type')
    
    if event_type in self.event_handlers:
      self.event_handlers[event_type](data)
      print(f"received {event_type}")
    else:
      print(f"Unhandled event type: {event_type}")

  # CHAT MESSAGE HANDLING
  def handle_chat_message(self, data):
    body = data['body']
    player = Player.objects.get(user=self.user)

    message = PokerMessages.objects.create(
      body=body,
      author = PokerPlayer.objects.get(player=player),
      room = self.pokerroom
    )

    event = {
      'type': 'send_chat_message',
      'message_id': message.id,
    }

    async_to_sync(self.channel_layer.group_send)(
      self.pokerroom_name, event
    )

  def send_chat_message(self, event):
    message_id = event['message_id']
    message = PokerMessages.objects.get(id=message_id)
    player = Player.objects.get(user=self.user)
    context = {
      'message': message,
      'user': PokerPlayer.objects.get(player=player),
      'type': 'message'
    }
    html = render_to_string('poker/partials/chat_message_p.html', context)
    self.send(text_data=html)

  # BROADCAST MESSAGE HANDLING
  def handle_broadcast_message(self, data):
    broadcast = PokerBroadcasts.objects.create(
      body=f'{self.user.username} {data}',
      room = self.pokerroom
    )
    event = {
      'type': 'send_broadcast_message',
      'broadcast_id': broadcast.id,
    }
    async_to_sync(self.channel_layer.group_send)(
      self.pokerroom_name, event
    )

  def send_broadcast_message(self, event):
    broadcast_id = event['broadcast_id']
    broadcast = PokerBroadcasts.objects.get(id=broadcast_id)
    context = {
      'broadcast': broadcast,
      'type': 'broadcast'
    }
    html = render_to_string('poker/partials/chat_message_p.html', context)
    self.send(text_data=html)

  # SEAT HANDLING
  def player_joined(self, data):
    pokerplayer_id = data['pokerplayer_data']['pokerplayer_id']
    pokerplayer = PokerPlayer.objects.get(id=pokerplayer_id)
    add_player_to_queue(self.pokerroom_name, pokerplayer)
    
    event = {
      'type': 'render_seat',
      'pokerplayer_id': pokerplayer_id
    }

    async_to_sync(self.channel_layer.group_send)(
      self.pokerroom_name, event
    )
  
  def render_seat(self, event):
    pokerplayer_id = event['pokerplayer_id']
    pokerplayer = PokerPlayer.objects.get(id=pokerplayer_id)

    # Renders the seat to everyone but the user who made the request
    if self.user.username != pokerplayer.player.user.username:
      queue = get_player_queue(self.pokerroom_name)
      seatnum = len(queue)-1

      context = {
        'username': pokerplayer.player.user.username,
        'stack': pokerplayer.stack,
        'seatnum': seatnum
      }
      html = render_to_string('poker/partials/seat_p.html', context)
      self.send(text_data=html)

  # Starting the game
  def handle_start_game(self, data):
    event = {
      'type': 'send_start_game'
    }
    
    async_to_sync(self.channel_layer.group_send)(
      self.pokerroom_name, event
    )
  
  def send_start_game(self, event):
    context = {
      'link': self.pokerroom_name
    }
    html = render_to_string('poker/partials/start_p.html', context)
    self.send(text_data=html)
