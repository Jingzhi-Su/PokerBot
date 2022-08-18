from deck import *
from discord.ext import commands

class Game:
    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.displayhand = []
        self.pot = 0
        self.current_bet = 0
        self.players_in_game = []

    """Adds a player instance to the game's player list"""
    def add_player(self, *args):
        for player in args:
            if type(player) == PlayerDiscordVer:
                self.players.append(player)
                self.players_in_game.append(player)
                print(f"Player {player.user} has been added.")
            else:
                print(f"Error, {player.user} could not be added")

    """Gives two cards to each player."""
    def give_hand_to_each_player(self):
        for player in self.players:
            player.draw(self.deck)
        
    """Dealer draws one card from the deck"""
    def draw_one(self):
        card = self.deck.draw(1)[0]
        self.displayhand.append(card)
    
    """Starts the round."""
    def start_round(self):
        assert self.players_in_game
        self.give_hand_to_each_player() 
        for player in self.players:
            player.money_betted += 10
        self.current_bet = 10
        for _ in range(3):
            self.draw_one()
            print(f"The current hand is {self.displayhand}")
            self.ask_player()
        self.assign_round_result()
        self.declare_winner()

    """Asks player if they want to raise, match, or fold."""    
    def ask_player(self, raise_player=None):
        for player in self.players_in_game:
            if player is raise_player:
                continue
            else:
                while True:
                    response = input(f"{player.name}, would you like to raise, match, or fold the current amount: {self.current_bet}?")
                    if response.lower() == "raise":
                        if player.total_money > self.current_bet:
                            self.player_move_raise(player)
                            self.ask_player(player)
                            return
                        else:
                            print("You do not have enough money to raise")
                    elif response.lower() == "match":
                        player.money_betted = self.current_bet
                        break
                    elif response.lower() == "fold":
                        self.players_in_game.remove(player)
                        break
                    else:
                        print("Please provid a valid input.")
    
    """Sorts a given hand based on default value"""
    def sort_player_hand(self, hand):
        """
        >>> hand = [
            Card("Hearts", "Ace", 14),
            Card("Spades", 8),
            Card("Diamonds", 6),
            Card("Clubs", 4),
            Card("Hearts", 2)
        ]
        >>> sort_player_hand(hand)
        [
            Card("Hearts", 2),
            Card("Clubs", 4),
            Card("Diamonds", 6),
            Card("Spades", 8),
            Card("Hearts", "Ace", 14)
        ]
        """
        new_hand = hand[:]
        new_hand.sort(key=lambda card: card.default_value)
        return new_hand
    
    """Assigns values to each player still in the game after the last card is drawn."""
    def assign_round_result(self):
        for player in self.players_in_game:
            hand = self.sort_player_hand(player.hand + self.displayhand)
            if (straight := self.check_straight(hand[:])) and self.check_flush(hand[:]):
                if straight[1] == 14:
                    player.round_result = (10, straight[1])
                else:
                    player.round_result = (9, straight[1])
            elif (four := self.check_number_matching(hand[:], 4)):
                player.round_result = (8, four[1])
            elif (full_house := self.check_full_house(hand[:])):
                player.round_result = (7, full_house[1])
            elif (flush := self.check_flush(hand[:])):
                player.round_result = (6, flush[1])
            elif (straight := self.check_straight(hand[:])):
                player.round_result = (5, straight[1])
            elif (three_of_a_kind := self.check_number_matching(hand[:], 3)):
                player.round_result = (4, three_of_a_kind[1])
            elif (two_pairs := self.check_two_pairs(hand[:])):
                player.round_result = (3, two_pairs[1])
            elif (pair := self.check_number_matching(hand[:], 2)):
                player.round_result = (2, pair[1])
            else:
                player.round_result = (1, self.check_high_card(hand[:]))

    """Compares the results of each player to declare a winner."""    
    def declare_winner(self):
        self.players_in_game.sort(key=lambda x: x.round_result[0])
        winner = self.players_in_game[0]
        for i in range(1, len(self.players_in_game)):
            tied_player = self.players_in_game[i]
            if tied_player.round_result == winner.round_result:
                winner = max(winner, tied_player, key=lambda x: x.round_result[1])
            else:
                break
        hand_name = self.match_ranking_to_hand(winner.round_result[0])
        print(f"The winner of this round is {winner.name} with {hand_name}!")
        self.add_pot_to_winner(winner)
        self.soft_reset()

    def match_ranking_to_hand(self, number):
        poker_hands ={
            10: "Royal Flush",
            9: "Straight Flush",
            8: "Four of a Kind",
            7: "Full House",
            6: "Flush",
            5: "Straight",
            4: "Three of a Kind",
            3: "Two Pairs",
            2: "Pair",
            1: "High Card"
        }
        return poker_hands[number]

    """Adds the winner's winnings to his total. Subtracts money_betted from everyone's total."""
    def add_pot_to_winner(self, winner):
        for player in self.players:
            self.pot += player.money_betted
            player.total_money -= player.money_betted
        winner.total_money += self.pot
        print(f"{winner.name} won {self.pot} this round.")


    """Given a sorted card hand and a number, returns whether the number of same cards matches the input number."""
    def check_number_matching(self, hand, number):
        """
        >>> hand = [
            Card("Clubs", "Ace", 14),
            Card("Hearts", "Ace", 14),
            Card("Spades", 9),
            Card("Diamonds", 8),
            Card("Clubs", 7)
        ]
        >>> check_number_matching(hand, 2)
        (True, 14)
        >>> hand = [
            Card("Clubs", "Ace", 14),
            Card("Hearts", "Ace", 14),
            Card("Spades", "Ace", 14),
            Card("Diamonds", 2),
            Card("Clubs", 7)
        ]
        >>> check_number_matching(hand, 3):
        (True, 14)
        >>> hand = [
            Card("Spades", "Ace", 14),
            Card("Hearts", "Ace", 14),
            Card("Diamonds", "Ace", 14),
            Card("Clubs", "Ace", 14),
            Card("Diamonds", 2)
        ]
        >>> check_number_matching(hand, 4)
        (True, 14)
        >>> hand = [
            Card("Hearts", "Ace", 14),
            Card("Spades", 8),
            Card("Diamonds", 6),
            Card("Clubs", 4),
            Card("Hearts", 2)
        ]
        >>> check_number_matching(hand, 2)
        False
        """
        carddict = {}
        for card in hand:
            if card.default_value not in carddict:
                carddict[card.default_value] = 1
            else:
                carddict[card.default_value] += 1
        for default_value in carddict:
            if carddict[default_value] == number:
                return (True, default_value)
        return False
    
    def check_full_house(self, hand):
        """
        >>> hand = [
            Card("Spades", "Ace", 14), 
            Card("Hearts", "Ace", 14), 
            Card("Diamonds", "Ace", 14), 
            Card("Hearts", "King", 13),
            Card("Spades", "King", 13)
        ]
        >>> check_full_house(hand)
        (True, 14)
        """
        triple = self.check_number_matching(hand, 3)
        if triple:
            pair = self.check_number_matching([card for card in hand if card.default_value != triple[1]], 2)
            if pair:
                return (True, triple[1])
        return False

    """checks for a flush given a hand. returns True if hand is a flush."""
    def check_flush(self, hand):
        """
        >>> hand = [
            Card("Hearts", 2),
            Card("Hearts", 4),
            Card("Hearts", 6),
            Card("Hearts", 8),
            Card("Hearts", "King", 13)
        ]
        >>> check_flush(hand)
        (True, 13)
        """
        suit = hand[0].suit
        if all([card.suit == suit for card in hand]):
            return (True, max([card.default_value for card in hand]))
        else:
            return False
    
    def check_straight(self, hand): 
        """
        >>> hand = [
            Card("Hearts", 5), 
            Card("Clubs", 6), 
            Card("Diamonds", 7), 
            Card("Spades", 8),
            Card("Hearts", 9)
        ]
        >>> check_straight(hand):
        (True, 9)
        """
        default_value_hand = [card.default_value for card in hand]
        for i in range(1, len(hand)):
            if default_value_hand[i] != default_value_hand[i - 1] + 1:
                return False
        return (True, default_value_hand[-1])

    def check_high_card(self, hand):
        """
        >>> hand = [
            Card("Hearts", "Ace", 14),
            Card("Spades", 8),
            Card("Diamonds", 6),
            Card("Clubs", 4),
            Card("Hearts", 2)
        ]
        >>> check_high_card(hand):
        14
        """
        return max([card.default_value for card in hand])

    def check_two_pairs(self, hand):
        """
        >>> hand = [
            Card("Diamonds", "King", 13),  
            Card("Clubs", "King", 13), 
            Card("Hearts", "Queen", 12),  
            Card("Spades", "Queen", 12),
            Card("Diamonds", "Jack", 11)
        ]
        >>> check_two_pair(hand)
        (True, 13)
        """
        pair = self.check_number_matching(hand, 2)
        if pair: 
            new_hand = [card for card in hand if card.default_value != pair[1]]
            second_pair = self.check_number_matching(new_hand, 2)
            if second_pair:
                return (True, max(pair[1], second_pair[1]))
        return False

    """Asks player how much he wants to raise the current_bet by."""
    def player_move_raise(self, player):
        while True:
            raise_amount = int(input(f"{player.name}, how much would you like to raise the current amount ({self.current_bet}) to?"))
            if raise_amount > self.current_bet and raise_amount < player.total_money:
                self.current_bet = raise_amount
                player.money_betted = self.current_bet
                break
            else:
                print(f"You need to input a number between {self.current_bet} and {player.total_money}.")
    
    """Soft reset the game without removing the players."""
    def soft_reset(self):
        self.deck = Deck()
        self.displayhand = []
        self.players_in_game = self.players[:]
        self.pot, self.current_bet = 0, 0
        for player in self.players:
            player.hand = []
            player.money_betted = 0
            player.round_result = None

class GameDiscordVer(Game):

    def __init__(self):
        super().__init__()
      
    def start_round(self, ctx):
        assert self.players_in_game
        for player in self.players_in_game:
            player.money_betted += 10
        self.current_bet = 10
        for _ in range(3):
            self.draw_one()
            ctx.send(f"The current hand is {self.displayhand}.")
            self.ask_player()

    def ask_player(self, ctx, raise_user):
        for player in self.players_in_game:
            if player.user is raise_user:
                continue
            else:
                while True:
                    def check(msg):
                        return msg.author == player.user and msg.channel == ctx.channel and msg.content.lower() in ["raise", "match", "fold"]
                    