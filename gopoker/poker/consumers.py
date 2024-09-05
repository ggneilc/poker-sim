from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from .models import *
import json

class PokerroomConsumer(WebsocketConsumer):
  def connect(self):
    self.user = self.scope['user']
    self.pokerroom_name = self.scope['url_route']['kwargs']['pokerroom_name']
    self.pokerroom = get_object_or_404(PokerRoom, name=self.pokerroom_name)

    async_to_sync(self.channel_layer.group_add)(
      self.pokerroom_name, self.channel_name
    )

    self.accept()

  def disconnect(self, code):
    async_to_sync(self.channel_layer.group_discard)(
      self.pokerroom_name, self.channel_name
    )

  def receive(self, text_data):
    text_data_json = json.loads(text_data)
    body = text_data_json['body']

    message = PokerMessages.objects.create(
      body=body,
      author = PokerPlayer.objects.get(user=self.user),
      room = self.pokerroom
    )

    # Event handler, type defines which method should handle each event
    event = {
      'type': 'message_handler',
      'message_id': message.id,
    }

    async_to_sync(self.channel_layer.group_send)(
      self.pokerroom_name, event
    )

  def message_handler(self, event):
    message_id = event['message_id']
    message = PokerMessages.objects.get(id=message_id)
    context = {
      'message': message,
      'user': PokerPlayer.objects.get(user=self.user),
    }
    html = render_to_string('poker/partials/chat_message_p.html', context)
    self.send(text_data=html)