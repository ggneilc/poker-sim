from django.db import models
from .utils import Card
from core.models import Player, Room

# Create your models here.


class BlackjackPlayer(models.Model):
    player = models.OneToOneField(Player,
                                  on_delete=models.CASCADE,
                                  related_name="blackjack_player")
    chips = models.IntegerField(default=0)
    has_blackjack = models.BooleanField(default=False)
    current_hand_value = models.IntegerField(default=0)

    hand = None
    curr_bet = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hand = []

    def recieveCard(self, card: 'Card'):
        self.hand.append(card)
        self.current_hand_value += card.getNum()

    def resetHand(self):
        self.hand.clear

    def __str__(self):
        return f"{super().__str__()} - Blackjack Score: {self.current_hand_value}"


class BlackjackRoom(Room):
    # Additional fields and methods specific to Blackjack rooms
    deck = models.JSONField(default=list)
    dealer_score = models.IntegerField(default=0)

    dealer_hand = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dealer_hand = []

    def recieveCard(self, card: 'Card'):
        self.dealer_hand.append(card)
        self.current_hand_value += card.getNum()

    def __str__(self):
        return f"{super().__str__()} - Dealer Score: {self.dealer_score}"
