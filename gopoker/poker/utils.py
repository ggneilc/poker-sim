'''
How to random: int(time.Now()) % 10 and subtract from randint.(52), then move to closest next available index (think hash map collision dection). This gives a temporary random that is better than a uniform distribution

We can also create games like blackjack with more decks in a similar fashion: 
d1,d2,d3,d4,d5,d6 = Deck()
shoe = [d1.shuffle(), d2.shuffle(), ..., d6.shuffle()]
# index shoe in the same way we index deck!
'''
import random, time
from enum import Enum, auto# utils.py
from django.core.cache import cache
from django.contrib.auth.models import User
from core.models import Player
from poker.models import *
import json

random.seed(time.time())

class Card:
    def __init__(self, x: int, s: int):
        self.num = x    # 1 2 3 4 5 6 7 8 9 10 11(J) 12(Q) 13(K)
        self.suit = s   # 1 (hearts) 2 (diamonds) 3 (spades) 4 (clubs)

    def getNum(self):
        return self.num

    def getNumString(self):
        switch={
            '1': 'Ace',
            '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7',
            '8': '8', '9': '9', '10': '10',
            '11': 'Jack',
            '12': 'Queen',
            '13': 'King',
        }
        return switch.get(str(self.num))

    def getSuit(self):
        return self.suit

    def getSuitString(self):
        switch={
            '1': 'Hearts',
            '2': 'Diamonds',
            '3': 'Spades',
            '4': 'Clubs',
        }
        return switch.get(str(self.suit))

    def toString(self):
        suit = self.getSuitString()
        num = self.getNumString()
        return f"{num} of {suit}"
    
    def to_dict(self):
        return {
            'num': self.num,
            'suit': self.suit
        }

    @staticmethod
    def newCard() -> 'Card':
        num = random.randint(1, 13) #randint is inclusive
        suit = random.randint(1,4)
        return Card(num, suit)

class Deck:
    def __init__(self): 
        self.count = 52
        self.cards = []
    
    def deal(self):
        '''Deal a single card to a player'''
        index = random.randint(1,52) - (int(time.time()) % 10) # random number
        if index > len(self.cards)-1:                     # boundaries
            index = len(self.cards) - 2
        elif index < 0:
            index = 0
        card = self.cards.pop(index)
        return card

    def shuffle(self):
        '''Initialize a new deck of cards'''              
        self.cards = []
        for i in range(1, 14): # Hearts 
            card = Card(i, 1)
            self.cards.append(card)
        for i in range(1, 14): # Diamonds
            card = Card(i, 2)
            self.cards.append(card)
        for i in range(1, 14): # Spades
            card = Card(i, 3)
            self.cards.append(card)
        for i in range(1, 14): # Clubs
            card = Card(i, 4)
            self.cards.append(card)

        # random literally has .shuffle()
        random.shuffle(self.cards)

    def toString(self):
        print(f"Remaining Cards: {len(self.cards)}\n")
        for i in self.cards:
            print(i.toString())

    def to_dict(self):
        return {
            'count': self.count,
            'cards': [card.to_dict() for card in self.cards]
        }
    
# Model Retrieval methods
# def get_poker_player(player):
#     # user = User.objects.get(username=username)
#     # player = Player.objects.get(user=user)
#     pokerplayer = PokerPlayer.objects.get(player=player)
#     return pokerplayer

# Player Queue Helper Methods
def get_room_queue_key(room_id):
    return f"player_queue_{room_id}"

def add_player_to_queue(room_id, player):
    key = get_room_queue_key(room_id)
    queue = cache.get(key, [])
    if player not in queue:
        queue.append(player)
        cache.set(key, queue)

def remove_player_from_queue(room_id, player):
    key = get_room_queue_key(room_id)
    queue = cache.get(key, [])
    if player in queue:
        queue.remove(player)
        cache.set(key, queue)

def get_player_queue(room_id):
    key = get_room_queue_key(room_id)
    return cache.get(key, [])