from django.shortcuts import render
from .utils import Card

# Create your views here.

def index(request):
    return render(request, 'index.html')

def hit(request):
    card = Card.newCard()
    context = { 
        "num": card.getNum(), 
        "suit": card.getSuit(),
        "card": card.toString()
    }
    return render(request, 'card.html', context)


def stand(request):
    return render(request, 'index.html')
