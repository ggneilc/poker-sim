from django.db import models
from .utils import Card

# Create your models here.


class Room(models.Model):
    STATUSES = {
        "O": "Open",
        "X": "Closed",
    }
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=1, choices=STATUSES, default="O")

    def __str__(self):
        return str(self.id)+", "+self.name+" : "+self.status


class Player(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField()
    outcome = models.IntegerField(default=0)  # 0 = lose/false, 1 = win/true
    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                             related_name="players",
                             default=1)
    hand = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hand = []

    def recieveCard(self, card: 'Card'):
        self.hand.append(card)

    def resetHand(self):
        self.hand.clear

    def __str__(self):
        d = f"{self.id} Name: {self.name} \tScore: {self.score}\nHand: "
        for x in self.hand:
            d = d + x.toString() + " "
        return d
