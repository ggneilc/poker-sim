from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    STATUSES = {
        "O": "Open",
        "X": "Closed",
    }
    GAMES = {
        "E": "EMPTY",
        "BJ": "Blackjack",
        "PK": "Poker",
        "CR": "Craps",
    }
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=1, choices=STATUSES, default="O")
    host = models.ForeignKey('Player', on_delete=models.SET_NULL,
                             null=True, blank=True,
                             related_name="hosted_room")
    game = models.CharField(max_length=2, choices=GAMES, default="E")

    def __str__(self):
        return f"{self.name} (Host: {self.host.name if self.host else 'No Host'}): {self.get_game_display()}, {self.get_status_display()} "


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                             related_name="players",
                             default=1)

    def __str__(self):
        return f"{self.id} Name: {self.user.username}"
