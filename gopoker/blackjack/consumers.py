from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from .utils import Deck
from blackjack.models import BlackjackPlayer, BlackjackRoom
from core.models import Player
import json
import asyncio
import redis.asyncio as redis


class BlackjackConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.player_id = None
        self.room_id = None
        self.room = None
        self.room_channel = None
        self.game_task = None

        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()

    async def connect(self):
        '''user connects to room'''
        self.user = self.scope['user']
        self.player_id = f"player_{self.user.id}"

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room = await self.get_BlackjackRoom(self.room_id)
        self.room_channel = f'blackjack_{self.room_id}'

        # Join Room Group
        await self.channel_layer.group_add(
            self.room_channel,
            self.channel_name
        )
        await self.accept()
        # Join Redis Channel
        await self.pubsub.subscribe(self.room_channel)
        await self.redis.sadd(f'{self.room_channel}_players', self.player_id)
        asyncio.create_task(self.listen_for_messages())
        print(f"{self.user} has connected & subscribed")
        print("listening for messages")

        # if empty room upon join, start game
        if await self.redis.scard(f'{self.room_channel}_players') == 1:
            self.game_task = asyncio.create_task(self.start_game())
            print("created game task")

    async def disconnect(self, code):
        '''user leaves websocket'''
        await self.pubsub.unsubscribe(self.room_channel)
        await self.redis.srem(f'{self.room_channel}_players', self.player_id)

        # if last player, kill game
        if await self.redis.scard(f'{self.room_channel}_players') == 0:
            self.game_task.cancel()
            print("game over")

        await self.channel_layer.group_discard(
            self.room_channel,
            self.channel_name
        )

    async def start_game(self):
        try:
            while True:
                await self.place_bets()
                await asyncio.sleep(5)
                await self.deal_cards()
                await asyncio.sleep(5)
                await self.player_actions()
                await asyncio.sleep(5)
                await self.dealer_action()
                await asyncio.sleep(5)
                await self.determine_winner()
                await asyncio.sleep(5)
                await self.reset()
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            await self.reset()
            print("killed game")

    async def place_bets(self):
        '''players place their bets'''
        # Publish betting active
        context = {'type': 'betting'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({
            'type': 'betting',
            'html': html
        }))
        while True:

            player_count = await self.redis.scard(f'{self.room_channel}_active_players')
            bet_count = await self.redis.scard(f'{self.room_channel}_bets')
            print(f'bets: {bet_count} players: {player_count}')

            if player_count == bet_count and player_count > 0:
                break

            await asyncio.sleep(1)

        # Publish betting is complete
        context = {'type': 'betting_complete'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

    async def deal_cards(self):
        '''deal hands to players'''
        print("dealing cards")
        await self.handle_hit(self.user)
        await self.handle_hit(self.user)
        await self.handle_stand(self.user)
        # Publish dealing
        context = {'type': 'dealing'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

    async def player_actions(self):
        '''players hit or stand'''
        print("players hit or stand")
        # Publish action
        context = {'type': 'paction'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

    async def dealer_action(self):
        '''dealer hits up to 17'''
        print("dealing to the dealer")
        await self.handle_stand(self.user)
        await self.handle_stand(self.user)
        context = {'type': 'daction'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

    async def determine_winner(self):
        '''check player hands and cmp to dealer'''
        print("determining winner")
        # Publish action
        context = {'type': 'end'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

    async def reset(self):
        '''remove all bets & hands'''
        print("starting new round...")
        # Publish action
        context = {'type': 'reset'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

        await self.redis.delete(
            f'{self.room_channel}_bets',
            f'{self.room_channel}_active_players'
        )

        # clear the board
        html = render_to_string('blackjack/clear_board.html')
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

    async def receive(self, text_data):
        '''receive ws message'''
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
            elif event_type == "bet":
                bet_amt = data.get('player-bet')
                await self.handle_bet(user, bet_amt)

    async def handle_bet(self, user, bet):
        '''handle a players bet'''
        player = await self.get_BlackjackPlayer(user)
        bet = int(bet)  # comes from json as string

        if bet is None or player.chips < bet:
            return 0

        player.chips -= int(bet)
        player.curr_bet = bet

        # register player as in the hand
        await self.redis.sadd(f'{self.room_channel}_active_players',
                              self.player_id)
        # save bet amount
        await self.redis.sadd(f'{self.room_channel}_bets', int(bet))

    async def handle_hit(self, player):
        '''handle a player hitting'''
        # Parse json representation of deck
        deck_dict = json.loads(self.room.deck)
        deck = Deck.from_dict(deck_dict)
        if deck.size() == 0:
            print("Deck is empty! reshuffling...")
            deck = Deck()
            deck.shuffle()
            self.room.deck = json.dumps(deck.to_dict())
            await self.save_DBObject(self.room)

        card = deck.deal()

        # parse player and add card to hand
        player = await self.get_BlackjackPlayer(self.user)
        player.recieveCard(card)
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
            self.room_channel,
            {
                'type': 'html_message',
                'html': html
            }
        )

    async def handle_stand(self, player):
        '''handle a player standing (deal card to dealer)'''
        # Parse json representation of deck
        deck_dict = json.loads(self.room.deck)
        deck = Deck.from_dict(deck_dict)
        if deck.size() == 0:
            print("Deck is empty! reshuffling...")
            deck = Deck()
            deck.shuffle()
            self.room.deck = json.dumps(deck.to_dict())
            await self.save_DBObject(self.room)

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
            self.room_channel,
            {
                'type': 'html_message',
                'html': html
            }
        )

    async def listen_for_messages(self):
        '''process redis pub/sub message'''
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                decoded_message = json.loads(message['data'].decode('utf-8'))
                # Now you can access the 'html' key
                await self.send(text_data=decoded_message['html'])

    async def game_message(self, event):
        '''send message to websocket'''
        await self.send(text_data=json.dumps(event['message']))

    async def html_message(self, event):
        '''sends html to the websocket client'''
        await self.send(text_data=event['html'])

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
