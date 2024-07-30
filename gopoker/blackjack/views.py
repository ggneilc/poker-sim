from django.shortcuts import render
from .import utils
from blackjack.models import Player, Room

# Create your views here.

# start the game on loading the page
def index(request):
    return render(request, 'index.html')

def start(request):
    '''create player & room'''
    username = request.POST.get('uname')
    score = request.POST.get('buyin')
    p = Player(name=username, score=score, outcome=0)
    p.save()
    context = {
        'name': username,
    }
    return render(request, 'player.html', context)

# hit to recieve another card
def hit(request):
    card = utils.Card.newCard()
    context = { 
        "num": card.getNum(), 
        "suit": card.getSuit(),
        "card": card.toString()
    }
    return render(request, 'card.html', context)


# moves action to dealer
def stand(request):
    return render(request, 'index.html')
