from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from .utils import Card
import json


class BlackjackConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        '''user connects to room'''
        self.user = self.scope['user']
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'blackjack_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"{self.user} has connected")

    async def disconnect(self, code):
        '''user leaves websocket'''
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        '''receive message'''
        data = json.loads(text_data)
        message_type = data.get('type')
        if message_type == 'player_action':
            event_type = data.get('event_type')
            user = data.get('user')

            # process different events
            if event_type == "hit":
                await self.handle_hit(user)
            elif event_type == "stand":
                await self.handle_stand(user)

    async def handle_hit(self, player):
        '''handle a player hitting'''
        card = Card.newCard()
        context = {
            "target": 'player',
            "num": card.getNum(),
            "suit": card.getSuit(),
            "card": card.toString()
        }
        html = render_to_string('blackjack/card.html', context)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'html_message',
                'html': html
            }
        )

    async def handle_stand(self, player):
        '''handle a player standing'''
        card = Card.newCard()
        context = {
            "target": 'dealer',
            "num": card.getNum(),
            "suit": card.getSuit(),
            "card": card.toString()
        }
        html = render_to_string('blackjack/card.html', context)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'html_message',
                'html': html
            }
        )

    async def game_message(self, event):
        '''send message to websocket'''
        await self.send(text_data=json.dumps(event['message']))

    async def html_message(self, event):
        '''sends html to the websocket client'''
        await self.send(text_data=event['html'])
#        await self.send(text_data=json.dumps({
#            "field": event['html']
#        }))
