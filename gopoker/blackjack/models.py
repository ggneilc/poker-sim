from django.db import models

# Create your models here.


class Room(models.Model):
    STATUSES = {
        "O": "Open",
        "X": "Closed",
    }
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=1, choices=STATUSES)

    def __str__(self):
        return str(self.id)+", "+self.name+" : "+self.status



class Player(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField()
    outcome = models.IntegerField() # 0 = False, 1 = True
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    hand = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hand = []

    def recieveCard(self, card: 'Card'):
        self.hand.append(card)

    def resetHand(self):
        self.hand.clear()
    
    def __str__(self):
        d = f"Score: {self.score}\nHand: "
        for x in self.hand:
            d = d + x.toString() + " "
        return d



