from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from . import utils
from blackjack.models import BlackjackPlayer, BlackjackRoom
from django.contrib.auth.models import User


# Choose to either join a friend or create new room
def index(request):
    return render(request, 'blackjack/index.html')


# Creates a blackjack room
def create_room(request):
    '''create new room at url'''
    room_id = request.POST.get('url')
    user = request.user
    player = BlackjackPlayer.objects.get(user=user)
    if not room_id:
        room_name = request.POST.get('room')
        r = BlackjackRoom(host=player, name=room_name, game="BJ")
        player.room = r
        r.save()
        player.save()
        response = JsonResponse({'status': 'success'})
        response['HX-Redirect'] = f'room/{r.id}'
        return response
    else:
        response = JsonResponse({'status': 'success'})
        response['HX-Redirect'] = f'room/{room_id}'
        return response


# Redirect to display the newly created room
def display_room(request, room_id):
    '''display the room at its id'''
    cur_room = BlackjackRoom.objects.get(pk=room_id)
    context = {
        'room': cur_room
    }
    return render(request, 'blackjack/room.html', context)


# Sit down at the blackjack table
#   Find the user's BlackjackPlayer 'account'
#   If not yet created, create it
#   else, update the player's buyin
def join_room(request, room_id):
    '''create player in room (sit down at table)'''
    room = BlackjackRoom.objects.get(pk=room_id)
    buyin = request.POST.get('buyin')

    user = request.user
    player, created = BlackjackPlayer.objects.get_or_create(user=user)
    player.chips = buyin
    player.room = room
    player.save()

    context = {
        'room': room,
        'name': user.username,
        'score': buyin,
    }
    return render(request, 'blackjack/player.html', context)


# hit to recieve another card
def hit(request, room_id):
    card = utils.Card.newCard()
    context = {
        "num": card.getNum(),
        "suit": card.getSuit(),
        "card": card.toString()
    }
    return render(request, 'blackjack/card.html', context)


# moves action to dealer
def stand(request, room_id):
    room = BlackjackRoom.objects.get(pk=room_id)
    card = utils.Card.newCard()
    context = {
        "num": card.getNum(),
        "suit": card.getSuit(),
        "card": card.toString()
    }
    room.dealer_score += card.getNum()
    room.save()
    return render(request, 'blackjack/card.html', context)
