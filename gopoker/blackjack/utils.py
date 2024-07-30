'''
How to random: int(time.Now()) % 10 and subtract from randint.(52), then move to closest next available index (think hash map collision dection). This gives a temporary random that is better than a uniform distribution

We can also create games like blackjack with more decks in a similar fashion: 
d1,d2,d3,d4,d5,d6 = Deck()
shoe = [d1.shuffle(), d2.shuffle(), ..., d6.shuffle()]
# index shoe in the same way we index deck!
'''
import random, time

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
        card = self.cards[index]
        self.cards.pop(index)
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




class Player:
    """Player has a hand, score, and outcome [win (True)/loss (False)]"""
    def __init__(self):
        self.hand = []
        self.score = 0
        self.outcome = False

    def recieveCard(self, card: 'Card'):
        self.hand.append(card)

    def resetHand(self):
        self.hand.clear()

    def updateScore(self, x):
        """if they lose x is negative, win x is positive"""
        self.score += x

    def win(self):
        self.outcome = True

    def lose(self):
        self.outcome = False

    def toString(self):
        d = f"Score: {self.score}\nHand: "
        for x in self.hand:
            d = d + x.toString() + " "
        return d

"""
Next Steps:
1. Create game object to keep track of game info
2. create views to use these methods
3. write templates to display the toString()s
"""

class Game:
    '''Stores information relating to current bj game'''
    def __init__(self):
        self.players = []   # empty room
        self.shoe = []      # no active decks
        self.status = True  # open room 
        self.action = None  # current player turn:
                            # after dealer, new round starts 

    def initShoe(self, x: int) -> None:
        '''add decks to the shoe'''
        self.shoe.clear()
        for i in range(x):
            deck = Deck()
            self.shoe.append(deck.shuffle())

    def addPlayer(self, p: 'Player') -> None:
        self.players.append(p)

    def removePlayer(self, p: 'Player') -> None:
        self.players.pop(p)

    def closeRoom(self):
        self.status = False

    def openRoom(self):
        self.status = True

    def startGame(self):
        '''set action to first player'''
        self.action = self.players[0]
        self.closeRoom()


if __name__ == "__main__":
    deck = Deck()
    p1 = Player()
    deck.shuffle()

    for i in range(5):
        p1.recieveCard(deck.deal())


    print(p1.toString())

