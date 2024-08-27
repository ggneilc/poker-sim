from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from . import utils
from blackjack.models import BlackjackPlayer, Room
from django.contrib.auth.models import User

# start the game on loading the page
def index(request):
    return render(request, 'blackjack/index.html')


def create_room(request):
    '''create new room at url'''
    room_id = request.POST.get('url')
    user = request.user
    if not room_id:
        name = request.POST.get('room')
        r = Room(host=user, name=name, game="BJ")
        r.save()
        response = JsonResponse({'status': 'success'})
        response['HX-Redirect'] = f'room/{r.id}'
        return response
    else:
        response = JsonResponse({'status': 'success'})
        response['HX-Redirect'] = f'room/{room_id}'
        return response


def display_room(request, room_id):
    '''display the room at its id'''
    cur_room = Room.objects.get(pk=room_id)
    context = {
        'room': cur_room
    }
    return render(request, 'blackjack/room.html', context)


def join_room(request, room_id):
    '''create player in room (sit down at table)'''
    room = Room.objects.get(pk=room_id)
    username = request.POST.get('uname')
    buyin = request.POST.get('buyin')

    u = User.objects.get(username=username)
    p = BlackjackPlayer(user=u, room=room, chips=buyin)
    p.save()
    context = {
        'name': username,
        'score': buyin,
    }
    return render(request, 'blackjack/player.html', context)


# hit to recieve another card
def hit(request):
    print("player hit")
    card = utils.Card.newCard()
    context = {
        "num": card.getNum(),
        "suit": card.getSuit(),
        "card": card.toString()
    }
    return render(request, 'blackjack/card.html', context)


# moves action to dealer
def stand(request):
    return render(request, 'blackjack/index.html')
