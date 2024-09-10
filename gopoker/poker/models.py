from django.db import models
from .utils import Card
from core.models import Player, Room


class PokerPlayer(models.Model):
    player = models.OneToOneField(Player,
                                  on_delete=models.CASCADE,
                                  related_name="poker_player")
    stack = models.FloatField(default=0)
    hand = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hand = []

    def recieveCard(self, card: 'Card'):
        self.hand.append(card)

    def resetHand(self):
        self.hand.clear

    def __str__(self):
        return f"{super().__str__()} - Stack: {self.stack}"


class PokerRoom(Room):
    # Additional fields and methods specific to Poker rooms
    deck = models.JSONField(default=list, blank=True)


class PokerMessages(models.Model):
    room = models.ForeignKey(PokerRoom,
                             related_name='chat_messages',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(PokerPlayer, on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.user.username} : {self.body}'

    class Meta:
        ordering = ['-created']
