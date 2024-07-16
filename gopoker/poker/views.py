from django.shortcuts import render
from utils import *

# Create your views here.

# start the game on loading the page
def index(request):
    return render(request, 'game.html')


# hit to recieve another card
def startGame(request):
    game.status = GameStatus.IN_PROGRESS
    # This should initiate the gameplay loop
    return render(request, 'start.html')

def pauseGame(request):
    game.status = GameStatus.PAUSED
    return render(request, 'pause.hmtl')

def stopGame(request):
    game.status = GameStatus.STOPPED
    return render(request, 'stop.hmtl')

# moves action to dealer
def stand(request):
    return render(request, 'game.html')
