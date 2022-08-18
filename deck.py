from email.policy import default
import random


class Card:

    def __init__(self, suit, number, default_value=None):
        self.suit = suit
        self.number = number
        if default_value is None:
            self.default_value = number
        else:
            self.default_value = default_value

    def __repr__(self):
        return f"{self.suit}-{self.number}"


class Deck:
    allcards = [
        Card("Spades", "Ace", 14),
        Card("Spades", 2),
        Card("Spades", 3),
        Card("Spades", 4),
        Card("Spades", 5),
        Card("Spades", 6),
        Card("Spades", 7),
        Card("Spades", 8),
        Card("Spades", 9),
        Card("Spades", 10),
        Card("Spades", "Jack", 11),
        Card("Spades", "Queen", 12),
        Card("Spades", "King", 13),
        Card("Hearts", "Ace", 14),
        Card("Hearts", 2),
        Card("Hearts", 3),
        Card("Hearts", 4),
        Card("Hearts", 5),
        Card("Hearts", 6),
        Card("Hearts", 7),
        Card("Hearts", 8),
        Card("Hearts", 9),
        Card("Hearts", 10),
        Card("Hearts", "Jack", 11),
        Card("Hearts", "Queen", 12),
        Card("Hearts", "King", 13),
        Card("Diamonds", "Ace", 14),
        Card("Diamonds", 2),
        Card("Diamonds", 3),
        Card("Diamonds", 4),
        Card("Diamonds", 5),
        Card("Diamonds", 6),
        Card("Diamonds", 7),
        Card("Diamonds", 8),
        Card("Diamonds", 9),
        Card("Diamonds", 10),
        Card("Diamonds", "Jack", 11),
        Card("Diamonds", "Queen", 12),
        Card("Diamonds", "King", 13),
        Card("Clubs", "Ace", 14),
        Card("Clubs", 2),
        Card("Clubs", 3),
        Card("Clubs", 4),
        Card("Clubs", 5),
        Card("Clubs", 6),
        Card("Clubs", 7),
        Card("Clubs", 8),
        Card("Clubs", 9),
        Card("Clubs", 10),
        Card("Clubs", "Jack", 11),
        Card("Clubs", "Queen", 12),
        Card("Clubs", "King", 13),
    ]

    def __init__(self):
        self.cards = Deck.allcards[:]
        self.num_cards = 52

    """Draws amount number of cards from the deck"""
    def draw(self, amount):
        resultcards = []
        if amount <= self.num_cards:
            for i in range(amount):
                resultcards.append(self.cards.pop(random.randint(0, self.num_cards)))
                self.num_cards -= 1
        return resultcards

class Player:
    def __init__(self, name, total_money=1000):
        self.name = name
        self.hand = []
        self.total_money = total_money
        self.round_result = None
        self.money_betted = 0

    def __repr__(self):
        return self.name
    
    """Player draws from the deck."""
    def draw(self, deck):
        self.hand.extend(deck.draw(2))

class PlayerDiscordVer(Player):
    def __init__(self, user):
        self.user = user
        self.hand = []
        self.total_money = 1000
        self.round_result = None
        self.money_betted = 0
        self.responded = False
    
    
    def __repr__(self):
        return self.user

    def draw(self, deck):
        super().draw(deck)


