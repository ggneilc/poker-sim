from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
# from asgiref.sync import async_to_sync
from .models import *
from poker.utils import *
import json
import asyncio
import redis.asyncio as redis


class PokerroomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.player_id = None
        self.pokerroom_id = None
        self.pokerroom = None

        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()

        self.event_handlers = {
            'chat_message': self.handle_chat_message,
            'player_joined': self.handle_player_joined,
            'start_game': self.handle_start_game
        }

    async def connect(self):
        self.user = self.scope['user']
        self.player_id = self.user.id

        self.pokerroom_id = self.scope['url_route']['kwargs']['room_id']
        self.pokerroom = await self.get_PokerRoom(self.pokerroom_id)

        # Join room group
        await self.channel_layer.group_add(
            self.pokerroom_id, self.channel_name
        )
        await self.accept()

        # TODO set up joining redis channel

        # Broadcast player joining the room
        await self.handle_broadcast_message("has joined")

    async def disconnect(self, code):
        # Discard player from room
        await self.channel_layer.group_discard(
            self.pokerroom_id, self.channel_name
        )

        # Broadcast player leaving
        await self.handle_broadcast_message("has left")

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')

        if event_type in self.event_handlers:
            await self.event_handlers[event_type](data)
            print(f"received {event_type}")
        else:
            print(f"Unhandled event type: {event_type}")

    # CHAT MESSAGE HANDLING
    async def handle_chat_message(self, data):
        body = data['body']
        poker_player = await self.get_PokerPlayer(self.user)

        message = await sync_to_async(PokerMessages.objects.create)(
            body=body,
            author=poker_player,
            room=self.pokerroom
        )

        event = {
            'type': 'send_chat_message',
            'message_id': message.id,
        }

        await self.channel_layer.group_send(
            self.pokerroom_id, event
        )

    async def send_chat_message(self, event):
        message_id = event['message_id']
        message = await sync_to_async(PokerMessages.objects.get)(id=message_id)
        poker_player = await self.get_PokerPlayer(self.user)
        context = {
            'message': message,
            'user': poker_player,
            'type': 'message'
        }
        html = await sync_to_async(render_to_string)('poker/partials/chat_message_p.html', context)
        await self.send(text_data=html)

    # BROADCAST MESSAGE HANDLING
    async def handle_broadcast_message(self, data):
        broadcast = await sync_to_async(PokerBroadcasts.objects.create)(
            body=f'{self.user.username} {data}',
            room=self.pokerroom
        )
        event = {
            'type': 'send_broadcast_message',
            'broadcast_id': broadcast.id,
        }
        await self.channel_layer.group_send(
            self.pokerroom_id, event
        )

    async def send_broadcast_message(self, event):
        broadcast_id = event['broadcast_id']
        broadcast = await sync_to_async(PokerBroadcasts.objects.get)(id=broadcast_id)
        context = {
            'broadcast': broadcast,
            'type': 'broadcast'
        }
        html = render_to_string('poker/partials/chat_message_p.html', context)
        await self.send(text_data=html)

    # SEAT HANDLING
    async def handle_player_joined(self, data):
        user_id = data['user_data']['user_id']
        user = await sync_to_async(User.objects.get)(id=user_id)
        pokerplayer = await self.get_PokerPlayer(user)
        sync_to_async(add_player_to_queue)(self.pokerroom_id, pokerplayer)

        event = {
            'type': 'send_player_joined',
            'user_id': user_id
        }

        await self.channel_layer.group_send(
            self.pokerroom_id, event
        )

    async def send_player_joined(self, event):
        user_id = event['user_id']
        user = await sync_to_async(User.objects.get)(id=user_id)
        pokerplayer = await self.get_PokerPlayer(user)
        html = ''

        queue = await sync_to_async(get_player_queue)(self.pokerroom_id)
        seatnum = await sync_to_async(len)(queue)-1
        
        username = await sync_to_async(lambda: pokerplayer.player.user.username)()
        buyin = await sync_to_async(lambda: pokerplayer.buyin)()
        stack = await sync_to_async(lambda: pokerplayer.stack)()
        net = stack-buyin
        

        context = {
            'username': username,
            'buyin': buyin,
            'stack': stack,
            'net': net,
            'seatnum': seatnum
        }

        # Renders the seat to everyone but the user who made the request
        if self.user.username != username:
            html = render_to_string('poker/partials/seat_p.html', context)

        html += render_to_string('poker/partials/ledger_p.html', context)
        await self.send(text_data=html)

    # Starting the game
    async def handle_start_game(self, data):
        '''Method is called from the host's client side "start game" button'''
        event = {
            'type': 'send_start_game'
        }

        await self.channel_layer.group_send(
            self.pokerroom_id, event
        )

    async def send_start_game(self, event):
        context = {
            'link': self.pokerroom_id
        }
        html = render_to_string('poker/partials/start_p.html', context)
        await self.send(text_data=html)

    @database_sync_to_async
    def get_PokerPlayer(self, user):
        '''Synchronous Database query for PokerPlayer'''
        try:
            p = Player.objects.get(user=user)
            player = PokerPlayer.objects.get(player=p)
            return player
        except Player.DoesNotExist:
            return None

    @database_sync_to_async
    def get_PokerRoom(self, room_id):
        '''Synchronous Database query for BlackjackRoom'''
        try:
            room = PokerRoom.objects.get(link=room_id)
            return room
        except PokerRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_DBObject(self, obj):
        '''Synchronous database query for saving object'''
        obj.save()
