from channels.generic.websocket import AsyncWebsocketConsumer
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
        event_type = data.get('event_type')
        player = data.get('player')

        # process different events
        if event_type == "hit":
            await self.handle_hit(player)
        elif event_type == "stand":
            await self.handle_stand(player)

    async def handle_hit(self, player):
        '''handle a player hitting'''

    async def handle_stand(self, player):
        '''handle a player standing'''

    async def game_message(self, event):
        '''send message to websocket'''
        await self.send(text_data=json.jumps(event['message']))
