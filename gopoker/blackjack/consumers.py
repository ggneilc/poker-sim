from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from .utils import Deck
from blackjack.models import BlackjackPlayer, BlackjackRoom
from core.models import Player
import json


class BlackjackConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        '''user connects to room'''
        self.user = self.scope['user']
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'blackjack_{self.room_id}'
        self.room = await self.get_BlackjackRoom(self.room_id)

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
        # Parse json representation of deck
        deck_dict = json.loads(self.room.deck)
        deck = Deck.from_dict(deck_dict)
        card = deck.deal()

        # parse player and add card to hand
        player = await self.get_BlackjackPlayer(self.user)
        player.recieveCard(card)
        player.current_hand_value += card.getNum()
        await self.save_DBObject(player)

        # update the rooms deck for the removed card
        self.room.deck = json.dumps(deck.to_dict())
        await self.save_DBObject(self.room)

        context = {
            "target": 'player',
            "num": card.getNumString(),
            "suit": card.getSuitString(),
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
        # Parse json representation of deck
        deck_dict = json.loads(self.room.deck)
        deck = Deck.from_dict(deck_dict)
        card = deck.deal()

        self.room.dealer_score += card.getNum()

        # update the rooms deck for the removed card
        self.room.deck = json.dumps(deck.to_dict())
        await self.save_DBObject(self.room)

        context = {
            "target": 'dealer',
            "num": card.getNumString(),
            "suit": card.getSuitString(),
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

    @database_sync_to_async
    def get_BlackjackPlayer(self, user):
        '''Synchronous Database query for BlackjackPlayer'''
        try:
            p = Player.objects.get(user=self.user)
            player = BlackjackPlayer.objects.get(player=p)
            return player
        except Player.DoesNotExist:
            return None

    @database_sync_to_async
    def get_BlackjackRoom(self, room_id):
        '''Synchronous Database query for BlackjackRoom'''
        try:
            room = BlackjackRoom.objects.get(link=room_id)
            return room
        except BlackjackRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_DBObject(self, obj):
        '''Synchronous database query for saving object'''
        obj.save()

    async def game_message(self, event):
        '''send message to websocket'''
        await self.send(text_data=json.dumps(event['message']))

    async def html_message(self, event):
        '''sends html to the websocket client'''
        await self.send(text_data=event['html'])
