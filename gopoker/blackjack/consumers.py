from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from .utils import Deck
from blackjack.models import BlackjackPlayer, BlackjackRoom
from django.contrib.auth.models import User
from core.models import Player
# from django.db import transaction
import json
import asyncio
import redis.asyncio as redis


class BlackjackConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_id = None
        self.room = None
        self.room_id = None
        self.room_channel = None
        # Conveience Variables
        self.seats = None
        # Asyncio Tasks toKill
        self.game_task = None
        self.listening = None
        # Redis
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()

    async def connect(self):
        '''user connects to room'''
        self.user = self.scope['user']
        self.user_id = self.user.id
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
        await self.redis.sadd(f'{self.room_channel}_players', self.user_id)
        self.listening = asyncio.create_task(self.listen_for_messages())
        print(f"{self.user} has connected & subscribed")
        print("listening for messages")
        # if empty room upon join, start game & set host
        if await self.redis.scard(f'{self.room_channel}_players') == 1:
            # TODO : get host
            self.game_task = asyncio.create_task(self.start_game())
            print("created game task")
        # register user channel name to receive personal messages
        await self.redis.hset('user_channel_map', self.user_id, self.channel_name)
        # publish that a user has joined
        await self.redis.publish(self.room_channel, json.dumps({'type': 'player_joined'}))

    async def disconnect(self, code):
        '''user leaves websocket'''
        try:  # leave redis communication pool
            print("leaving connection pool...")
            try:
                await self.redis.srem(f'{self.room_channel}_players', self.user_id)
                await self.redis.publish(self.room_channel, json.dumps({'type': 'player_left'}))
                await self.pubsub.unsubscribe(self.room_channel)
                await self.redis.hdel('user_channel_map', self.user_id)
            except Exception as e:
                print(f"Error during connection pool disconnect: {e}")

            print("left connection pool")
            try:
                self.listening.cancel()
                await self.listening
            except Exception as e:
                print(f"Error during listening: {e}")
            print("stopped listening")

            # reset the players' info -> we already removed them so reset won't
            bjplayer = await self.get_BlackjackPlayer(self.user)
            bjplayer.current_hand_value = 0
            await self.save_DBObject(bjplayer)
            print("reset player")

            # if last player, kill game
            if await self.redis.scard(f'{self.room_channel}_players') == 0:
                self.game_task.cancel()
                await self.game_task  # immediately call task to process cancel
                print("game over")

        except Exception as e:
            print(f"Error during disconnect: {e}")

        finally:  # close redis client
            try:
                await self.redis.aclose()
                await self.pubsub.aclose()
                print("closed redis connection")
            except Exception as redis_error:
                print(f"Error closing redis connection: {redis_error}")

            await self.channel_layer.group_discard(
                self.room_channel,
                self.channel_name
            )

    async def start_game(self):
        try:
            while True:
                try:
                    await self.place_bets()
                    await self.deal_cards()
                    await asyncio.sleep(1)
                    await self.player_actions()
                    await self.dealer_action()
                    await self.determine_winner()
                    await asyncio.sleep(3)
                    await self.reset()
                    await asyncio.sleep(3)
                except asyncio.CancelledError:
                    print("game recieved cancellation")
                    raise
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
            player_count = await self.redis.scard(f'{self.room_channel}_players')
            aplayer_count = await self.redis.scard(f'{self.room_channel}_active_players')
            bet_count = await self.redis.scard(f'{self.room_channel}_bets')
            print(f'bets: {bet_count} players: {player_count}')
            if player_count == bet_count and aplayer_count > 0 and player_count == aplayer_count:
                break
            await asyncio.sleep(1)
        # Publish betting is complete
        context = {'type': 'betting_complete'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))

    async def deal_cards(self):
        '''deal hands to players'''
        print("dealing cards")
        user_ids = await self.redis.smembers(f'{self.room_channel}_active_players')
        # deal 2 cards to each active player
        for user_id in user_ids:
            user = await self.get_UserObject(id=user_id)
            print(f'dealing card to {user} with id {user_id}')
            await self.deal_card(user, user_id)
            await self.deal_card(user, user_id)

        # deal a card to the dealer
        await self.dealer_card()

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
        while True:
            stood_count = await self.redis.scard(f'{self.room_channel}_stood')
            player_count = await self.redis.scard(f'{self.room_channel}_active_players')
            print(f'stood_count : {stood_count}, players in hand : {player_count}')

            if (stood_count == player_count):
                break

            await asyncio.sleep(1)

    async def dealer_action(self):
        '''dealer hits up to 17'''
        print("dealing to the dealer")
        context = {'type': 'daction'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))
        while self.room.dealer_score < 17:
            await self.dealer_card()
            await asyncio.sleep(3)

    async def determine_winner(self):
        '''check player hands and cmp to dealer'''
        print("determining winner")
        # Publish action
        context = {'type': 'end'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))
        player_count = await self.redis.scard(f'{self.room_channel}_active_players')
        # dealer did not bust & players are still in the hand
        if (self.room.dealer_score < 22 and player_count > 0):
            # parse players in the hand and payout chips
            user_ids = await self.redis.smembers(f'{self.room_channel}_active_players')
            for user_id in user_ids:
                user = await self.get_UserObject(id=int(user_id))
                bjplayer = await self.get_BlackjackPlayer(user)
                print(f'player_hand : {bjplayer.current_hand_value}')
                # player wins
                if (bjplayer.current_hand_value > self.room.dealer_score):
                    payout = int(bjplayer.curr_bet) * 2
                    bjplayer.chips += payout
                    await self.save_DBObject(bjplayer)
                # player pushes
                elif (bjplayer.current_hand_value == self.room.dealer_score):
                    bjplayer.chips += bjplayer.curr_bet
                    await self.save_DBObject(bjplayer)
                # if player lost, they already out of hand
        # dealer busts but players still in hand
        elif (self.room.dealer_score > 21 and player_count > 0):
            # parse players in the hand and payout chips
            user_ids = await self.redis.smembers(f'{self.room_channel}_active_players')
            for user_id in user_ids:
                user = await self.get_UserObject(id=int(user_id))
                bjplayer = await self.get_BlackjackPlayer(user)
                # player wins
                payout = int(bjplayer.curr_bet) * 2
                bjplayer.chips += payout
                await self.save_DBObject(bjplayer)

    async def reset(self):
        '''remove all bets & hands'''
        print("reseting room")
        # Publish action
        context = {'type': 'reset'}
        html = render_to_string('blackjack/game_message.html', context)
        await self.redis.publish(self.room_channel, json.dumps({'html': html}))
        # Update player chips
        user_ids = await self.redis.smembers(f'{self.room_channel}_active_players')
        for user_id in user_ids:
            user = await self.get_UserObject(id=user_id)
            user_channel = await self.redis.hget('user_channel_map', user_id)
            print(f'{user_id} {user} {user_channel}')
            bjplayer = await self.get_BlackjackPlayer(user)
            context = {'name': user.username, 'chips': bjplayer.chips, 'user': user}
            html = render_to_string('blackjack/player.html', context)
            await self.channel_layer.send(
                user_channel.decode('utf-8'),
                {
                    'type': 'html_message',
                    'html': html
                }
            )
        await self.redis.delete(
            f'{self.room_channel}_bets',
            f'{self.room_channel}_active_players',
            f'{self.room_channel}_stood'
        )
        # reset dealer_hand
        self.room.dealer_score = 0
        await self.save_DBObject(self.room)
        # reset players current hand to 0:
        player_count = await self.redis.scard(f'{self.room_channel}_players')
        if (player_count > 0):
            player_ids = await self.redis.smembers(f'{self.room_channel}_players')
            for player_id in player_ids:
                bjplayer = await self.get_BlackjackPlayer(player_id)
                bjplayer.current_hand_value = 0
                await self.save_DBObject(bjplayer)
            # clear the board
            html = render_to_string('blackjack/clear_board.html')
            await self.redis.publish(self.room_channel, json.dumps({'html': html}))
        print("Finished reset")

    async def receive(self, text_data):
        '''receive ws message'''
        data = json.loads(text_data)
        message_type = data.get('type')
        if message_type == 'player_action':
            event_type = data.get('event_type')
            user = data.get('user')
            print(user)
            # process different events
            if event_type == "hit":
                await self.handle_hit(user)
            elif event_type == "stand":
                await self.handle_stand(user)
            elif event_type == "bet":
                bet_amt = data.get('player-bet')
                await self.handle_bet(user, bet_amt)

    async def handle_bet(self, username, bet):
        '''handle a players bet'''
        user = await self.get_UserObject(username=username)
        player = await self.get_BlackjackPlayer(user)
        bet = int(bet)  # comes from json as string
        # TODO : return snippet saying not enough chips
        if bet is None or player.chips < bet:
            return 0
        player.chips -= int(bet)
        player.curr_bet = bet
        print(f"{user} placed bet: {player.curr_bet}")
        await self.save_DBObject(player)
        # register player as in the hand
        await self.redis.sadd(f'{self.room_channel}_active_players',
                              self.user_id)
        # save bet amount
        await self.redis.sadd(f'{self.room_channel}_bets', int(bet))
        # update frontend player chips
        context = {
            'name': user.username,
            'chips': player.chips,
            'user': user
        }
        html = render_to_string('blackjack/player.html', context)
        await self.channel_layer.send(
            self.channel_name,
            {
                'type': 'html_message',
                'html': html
            }
        )

    async def handle_hit(self, username):
        '''handle a player hitting'''
        # Parse json representation of deck
        card, face = await self.get_card()
        # parse player and add card to hand
        print(username)
        user = await self.get_UserObject(username=username)
        player = await self.get_BlackjackPlayer(user)
        player.recieveCard(card)
        print(f"{player} associated with {user.username} has {player.current_hand_value}")
        await self.save_DBObject(player)
        await self.send_card('player', card, face, user_id=user.id)
        # handle player busting : leave the active_players
        if (player.current_hand_value > 21):  # player busts
            await self.redis.srem(f'{self.room_channel}_active_players', user.id)

    async def handle_stand(self, username):
        '''handle a player standing (deal card to dealer)'''
        # register player as stood
        user = await self.get_UserObject(username=username)
        await self.redis.sadd(f'{self.room_channel}_stood', user.id)

    async def deal_card(self, user, user_id):
        '''deal a card to a specific user'''
        # Parse json representation of deck
        card, face = await self.get_card()
        # parse player and add card to hand
        player = await self.get_BlackjackPlayer(user)
        player.recieveCard(card)
        await self.save_DBObject(player)
        # Send card to user's frontend
        await self.send_card('player', card, face, user_id=user_id)

    async def dealer_card(self):
        '''deal a card to the dealer'''
        # Parse json representation of deck
        card, face = await self.get_card()
        self.room.dealer_score += card.getNum()
        await self.send_card('dealer', card, face, channel=self.room_channel)

    def calculate_seat_map(self, user, user_ids):
        '''calculate arrangement of seats around user'''
        user_ids = {int(uid.decode('utf-8')) for uid in user_ids}
        user = int(user.decode('utf-8')) if isinstance(user, bytes) else user
        ordered_ids = list(user_ids)
        ordered_ids.remove(user)
        ordered_ids.insert(0, user)

        seat_map = {}
        # start at 1,2,3
        for idx, user_id in enumerate(ordered_ids):
            seat_map[user_id] = f'player{idx+1}'

        print(seat_map)
        return seat_map

    async def listen_for_messages(self):
        '''process redis pub/sub message'''
        try:
            while True:
                try:
                    message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        decoded_message = json.loads(message['data'].decode('utf-8'))

                        if 'type' in decoded_message and (decoded_message.get('type') == 'player_joined' or decoded_message.get('type') == 'player_left'):
                            print("new player joined")
                            user_ids = await self.redis.smembers(f'{self.room_channel}_players')
                            self.seats = self.calculate_seat_map(self.user_id, user_ids)
                            await self.redis.hset(f'{self.room_channel}_seats', self.user_id, json.dumps(self.seats))
                            print("calculated seat map")
                        elif 'html' in decoded_message:
                            await self.send(text_data=decoded_message['html'])
                    await asyncio.sleep(0.1)  # prevent tight loop -> Allows cancelation
                except asyncio.CancelledError:
                    print("Listen task received cancellation")
                    raise  # Re-raise to properly handle cancellation
                except Exception as e:
                    print(f"Error in listen loop: {e}")
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("Listen task clean up")


    async def game_message(self, event):
        '''send message to websocket'''
        await self.send(text_data=json.dumps(event['message']))

    async def html_message(self, event):
        '''sends html to the websocket client'''
        await self.send(text_data=event['html'])

    # Channel is to broadcast for dealer hitting
    # user-id is used for hitting and initial deal
    async def send_card(self, target, card, face, channel=None, user_id=None):
        if user_id:  # Personal Message -> this player is main player
            seats = await self.get_seat_map(user_id)
            print(f'retrived seat map: {seats}')
            for id, target in seats.items():  # populate template and send to specific user channel
                print(f'got id {id} and sending to {target}')
                uchannel = await self.redis.hget('user_channel_map', id)
                # if target != player1, send mini card
                context = {
                    "target": target,
                    "num": face,
                    "suit": card.getSuitString(),
                    "card": card.toString()
                }
                html = render_to_string('blackjack/card.html', context)
                await self.channel_layer.send(
                    uchannel.decode('utf-8'),
                    {
                        'type': 'html_message',
                        'html': html
                    }
                )
        else:  # Group Message
            context = {
                "target": target,
                "num": face,
                "suit": card.getSuitString(),
                "card": card.toString()
            }
            html = render_to_string('blackjack/card.html', context)
            await self.channel_layer.group_send(
                channel,
                {
                    'type': 'html_message',
                    'html': html
                }
            )

    async def get_card(self):  # async because we need to save the room
        deck_dict = json.loads(self.room.deck)
        deck = Deck.from_dict(deck_dict)
        if deck.size() == 0:
            print("Deck is empty! reshuffling...")
            deck = Deck()
            deck.shuffle()
            self.room.deck = json.dumps(deck.to_dict())
            await self.save_DBObject(self.room)
        card = deck.deal()
        face = card.getNumString()
        # Face cards all equal 10
        if (card.getNum() > 10):
            card.num = 10
        self.room.deck = json.dumps(deck.to_dict())
        await self.save_DBObject(self.room)
        return card, face

    async def get_seat_map(self, user_id):
        seat_json = await self.redis.hget(f'{self.room_channel}_seats', user_id)
        return json.loads(seat_json) if seat_json else None

    @database_sync_to_async
    def get_UserObject(self, id=None, username=None):
        '''Synchronous Database query for BlackjackPlayer'''
        try:
            if username is not None:
                p = User.objects.get(username=username)
                return p
            if id is not None:
                p = User.objects.get(id=id)
                return p
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_BlackjackPlayer(self, user):
        '''Synchronous Database query for BlackjackPlayer'''
        try:
            p = Player.objects.get(user=user)
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
