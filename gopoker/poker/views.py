from django.shortcuts import render
from django.http import HttpResponse
from . import utils


# Create your views here.

# start the game on loading the page
def index(request):
    # game.status = GameStatus.SETUP
    # if player == host:
    #   render(start and pause buttons)
    return render(request, 'poker/game.html')


# Activated when start game button is clicked
# Will populate the table felt
def startGame(request):
    # game.status = GameStatus.IN_PROGRESS
    # This should initiate the gameplay loop
    context = {
        'button': render(request, 'stop.html').content.decode(),
        'board': render(request, 'felt.html').content.decode(),
        'info': render(request, 'player_options.html').content.decode(),
    }
    return render(request, 'poker/start.html', context)


def pauseGame(request):
    # game.status = GameStatus.PAUSED
    return render(request, 'poker/pause.hmtl')

def stopGame(request):
    # game.status = GameStatus.STOPPED
    return render(request, 'poker/stop_game.html')


# ---------------------------------------------------
# Player action logic

def raiseBet(request):
    return render(request, 'poker/raise.html')
