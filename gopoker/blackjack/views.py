from django.shortcuts import render
from django.http import HttpResponse
from .utils import Deck
from blackjack.models import BlackjackPlayer, BlackjackRoom
from core.models import Player
from core.views import genRandomID
import json


# Choose to either join a friend or create new room
def index(request):
    # create a base room
    user = request.user
    player = Player.objects.get(user=user)
    if player.room is not None:
        response = HttpResponse()
        response['HX-redirect'] = f'/blackjack/room/{player.room.link}'
        return response
    else:
        deck = Deck()
        deck.shuffle()
        link = genRandomID()
        bjRoom = BlackjackRoom(host=player,
                               link=link,
                               game="BJ",
                               deck=json.dumps(deck.to_dict()))
        bjRoom.save()
        response = HttpResponse()
        response['HX-redirect'] = f'/blackjack/room/{link}'
        return response


# Redirect to display the newly created room
def display_room(request, room_id):
    '''display the room at its id'''
    cur_room = BlackjackRoom.objects.get(link=room_id)
    context = {
        'room': cur_room
    }
    return render(request, 'blackjack/index.html', context)


# Sit down at the blackjack table
#   Find the user's BlackjackPlayer 'account'
#   If not yet created, create it
#   else, update the player's buyin
def join_room(request, room_id):
    '''create blackjackplayer in room (sit down at table)'''
    room = BlackjackRoom.objects.get(link=room_id)
    buyin = request.POST.get('buyin')

    # get the Player from the user (request)
    user = request.user
    player = Player.objects.get(user=user)
    player.room = room
    player.save()

    # get the players' BlackjackPlayer
    bjplayer, created = BlackjackPlayer.objects.get_or_create(player=player)
    bjplayer.chips = buyin
    bjplayer.save()

    context = {
        'room': room,
        'name': user.username,
        'chips': buyin,
    }
    return render(request, 'blackjack/player.html', context)


# removes the user from the current room
def leave_room(request, room_id):
    '''leave the current room'''
    user = request.user
    player = Player.objects.get(user=user)
    player.room = None  # 1 is the default room
    player.save()
    response = HttpResponse()
    response['HX-redirect'] = r'/'
    return response
