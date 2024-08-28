from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from . import utils
from poker.models import *
from poker.forms import ChatmessageCreateForm


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
        'button': render(request, 'poker/stop.html').content.decode(),
        'board': render(request, 'poker/felt.html').content.decode(),
        'info': render(request, 'poker/player_options.html').content.decode(),
    }
    return render(request, 'poker/start.html', context)

# TODO Establish rooms

def pauseGame(request):
    # game.status = GameStatus.PAUSED
    return render(request, 'poker/pause.hmtl')

def stopGame(request):
    # game.status = GameStatus.STOPPED
    return render(request, 'poker/stop_game.html')

def raiseBet(request):
    return render(request, 'poker/raise.html')

# CHAT FEATURE
def chatView(request):
    poker_room = get_object_or_404(PokerRoom, name="room1")
    chat_messages = poker_room.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

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
            return render(request, 'poker/chat_message.html', context)

    return render(request, 'poker/chat.html', {'chat_messages' : chat_messages, 'form' : form})