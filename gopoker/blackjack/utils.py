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
        pass

    def shuffle(self):
        pass

