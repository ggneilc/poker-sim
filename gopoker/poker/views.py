from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .utils import *
from poker.models import *
from poker.forms import ChatmessageCreateForm
from core.models import Player
from core.views import genRandomID
import json


# Create your views here.

# start the game on loading the page
def index(request):
    user = request.user
    player = Player.objects.get(user=user)
    if player.room is not None:
        response = HttpResponse()
        response['HX-redirect'] = f'/poker/room/{player.room.link}'
        return response
    else:
        deck = Deck()
        deck.shuffle()
        link = genRandomID()
        poker_room = PokerRoom(host=player,
                               link=link,
                               game="PK",
                               deck=json.dumps(deck.to_dict()))
        poker_room.save()

        poker_player, created = PokerPlayer.objects.get_or_create(player=player)
        poker_player.host = True
        poker_player.save()
        response = HttpResponse()
        response['HX-redirect'] = f'/poker/room/{link}'
        return response

# Redirect to display the newly created room
def displayRoom(request, room_id):
    '''display the room at its id'''
    player = Player.objects.get(user=request.user)
    poker_player, created = PokerPlayer.objects.get_or_create(player=player)
    cur_room = PokerRoom.objects.get(link=room_id)
    print("DISPLAYING ROOM")
    context = {
        'room': cur_room,
        'cur_pokerplayer': poker_player,
        'player_queue': cur_room.player_queue
    }
    return render(request, 'poker/game.html', context)


def joinRoom(request, room_id):
    '''create blackjackplayer in room (sit down at table)'''
    room = PokerRoom.objects.get(link=room_id)
    nickname = request.POST.get('nickname')
    buyin = request.POST.get('buyin')

    # get the Player from the user (request)
    user = request.user
    player = Player.objects.get(user=user)
    player.room = room
    player.save()

    # get the players' PokerPlayer
    pokerplayer = PokerPlayer.objects.get(player=player)
    pokerplayer.stack = buyin
    pokerplayer.save()

    # notify websocket that player joined
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room_id,
        {
            'type': 'player_joined',
            'pokerplayer': pokerplayer
        }
    )

    context = {
        'room': room,
        'nickname': nickname,
        'stack': buyin,
    }

    return render(request, 'poker/player.html', context)


def leaveRoom(request, room_id):
    '''leave the current room'''
    user = request.user
    player = Player.objects.get(user=user)
    player.room = None
    player.save()
    response = HttpResponse()
    response['HX-redirect'] = r'/'
    return response

# Renders a new players seat to the screen
def renderSeat(request, player_id):
   print('hey')
   poker_player = get_object_or_404(PokerPlayer, id=player_id)
   context = {
       'poker_player': poker_player
   }
   return render(request, 'poker/seat_p.html', context)

# Activated when start game button is clicked
# Will populate the table felt
def startGame(request, room_id):
    # game.status = GameStatus.IN_PROGRESS
    # This should initiate the gameplay loop
    context = {
        'button': render(request, 'poker/stop.html').content.decode(),
        'board': render(request, 'poker/felt.html').content.decode(),
        'info': render(request, 'poker/player_options.html').content.decode(),
        'link': room_id
    }
    return render(request, 'poker/start.html', context)

# TODO Establish rooms

def pauseGame(request):
    # game.status = GameStatus.PAUSED
    return render(request, 'poker/pause.hmtl')

def stopGame(request, room_id):
    # game.status = GameStatus.STOPPED
    return render(request, 'poker/stop_game.html')

def raiseBet(request):
    return render(request, 'poker/raise.html')

# CHAT FEATURE
def chatView(request, room_id):
    poker_room = get_object_or_404(PokerRoom, link=room_id)
    chat_messages = poker_room.chat_messages.all()[:30]
    form = ChatmessageCreateForm()
    context = {
        'chat_messages' : chat_messages, 
        'form' : form,
        'room' : poker_room
    }

    if request.method == 'POST':
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid:
            print("saving?")
            message = form.save(commit=False)
            message.author = PokerPlayer.objects.get(user=request.user)
            message.room = poker_room
            message.save()
            context = {
                'message' : message,
                'user' : request.user
            }
            return render(request, 'poker/partials/chat_message_p.html', context)

    return render(request, 'poker/chat.html', context)