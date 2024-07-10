from django.shortcuts import render
from .utils import Card

# Create your views here.

# start the game on loading the page
def index(request):
    return render(request, 'index.html')


# hit to recieve another card
def hit(request):
    card = Card.newCard()
    context = { 
        "num": card.getNum(), 
        "suit": card.getSuit(),
        "card": card.toString()
    }
    return render(request, 'card.html', context)


# moves action to dealer
def stand(request):
    return render(request, 'index.html')
