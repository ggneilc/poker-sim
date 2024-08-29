from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import *
import json

class PokerroomConsumer(WebsocketConsumer):
  def connect(self):
    self.user = self.scope['user']
    self.pokerroom_name = self.scope['url_route']['kwargs']['pokerroom_name']
    self.pokerroom = get_object_or_404(PokerRoom, name=self.pokerroom_name)
    self.accept()

  def receive(self, text_data):
    text_data_json = json.loads(text_data)
    body = text_data_json['body']

    message = PokerMessages.objects.create(
      body=body,
      author = PokerPlayer.objects.get(user=self.user),
      room = self.pokerroom
    )
    context = {
      'message': message,
      'user': self.user,
    }
    html = render_to_string('poker/chat_message.html', context)
    self.send(text_data=html)