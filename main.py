import string
import discord
from discord.ext import commands
from game import Game, GameDiscordVer
from deck import *
import asyncio

TOKEN = ""

bot = commands.Bot( command_prefix = "&")

game = GameDiscordVer()

@bot.event
async def on_ready():
    print("Poker Bot Online")

@bot.command()
async def test(ctx):
    await ctx.send("This tests functions. Say yes to continue.")
    def check(msg):       
        return msg.author == ctx.author and msg.channel == ctx.channel
    msg = await bot.wait_for("message", check=check)
    if msg.content.lower() == "yes":
        await ctx.invoke(bot.get_command("test2"))
        await ctx.send("This should come after.")
    else:
        await ctx.send("No")

@bot.command()
async def test2(ctx):
    await ctx.send("Are you sure?")
    def check(msg):       
        return msg.author == ctx.author and msg.channel == ctx.channel
    msg = await bot.wait_for("message", check=check)
    await ctx.send("okay")

@bot.command()
async def test3(ctx):
    await ctx.send("This is to test numbers. Please reply with a number below.")
    def check(msg):       
        return msg.author == ctx.author and msg.channel == ctx.channel
    msg = await bot.wait_for("message", check=check)
    msg = int(msg.content)
    await ctx.send(msg + 3)



@bot.command()
async def join(ctx, user: discord.Member):
    player = PlayerDiscordVer(user)
    game.add_player(player)
    await ctx.send(f"{user} has joined the game.")
    
    
    
@bot.command()
async def give_hand(ctx):
    for player in game.players_in_game:
        player.draw(game.deck)
        await player.user.send(f"Your hand is {player.hand}.")


@bot.command()
async def start(ctx):

    await ctx.invoke(bot.get_command("give_hand"))

    for player in game.players_in_game:
        player.money_betted += 10
    
    game.current_bet = 10
    for _ in range(3):
        game.draw_one()
        await ctx.send(f"The current hand is {game.displayhand} and the current highest bet is {game.current_bet}.")
        await ctx.invoke(bot.get_command("ask_player"))
    game.assign_round_result()
    print("before")
    await ctx.invoke(bot.get_command("declare_winner"))
    print("after")

@bot.command()
async def ask_player(ctx, raise_user=None):

    for player in game.players_in_game:

            if player == raise_user:
                continue

            else:

                def check(msg):
                    return msg.author == player.user and msg.channel == ctx.channel and msg.content.lower() in ["raise", "match", "fold"]

                while True:

                    await ctx.send(f"{player.user}, would you like to raise, match, or fold the current bet: {game.current_bet}?")
                    msg = await bot.wait_for("message", check=check)

                    if msg.content.lower() == "raise":

                        if player.total_money > game.current_bet:
                            await ctx.invoke(bot.get_command("player_move_raise"), player=player)
                            await ctx.invoke(bot.get_command("ask_player"), raise_user=player)
                            return

                        else:
                            await ctx.send("You do not have enough money to raise")


                    elif msg.content.lower() == "match":
                        if player.total_money > game.current_bet:
                            player.money_betted = game.current_bet
                        else:
                            await ctx.send("You do not have enough money to match the current amount. Therefore, you will exit the game")
                            game.player_in_game.remove(player)
                        break
                        
                    elif msg.content.lower() == "fold":
                        game.players_in_game.remove(player)
                        break

                    else:
                        await ctx.send("Please provide a valid input")




@bot.command()
async def player_move_raise(ctx, player):

    def check(msg):
        return msg.author == player.user and msg.channel == ctx.channel
    
    while True:

        await ctx.send(f"{player.user}, how much would you like to raise the current amount ({game.current_bet}) to?")

        msg = await bot.wait_for("message", check=check)
        msg = int(msg.content)

        if msg > game.current_bet and msg < player.total_money:
            game.current_bet = msg
            player.money_betted = game.current_bet
            break

        else:
            ctx.send(f"You need to input a number between {game.current_bet} and {player.total_money}.")




@bot.command()
async def declare_winner(ctx):

    game.players_in_game.sort(key=lambda x: x.round_result[0])
    winner = game.players_in_game[0]

    for i in range(1, len(game.players_in_game)):

        tied_player = game.players_in_game[i]
        if tied_player.round_result == winner.round_result:
            winner = max(winner, tied_player, key=lambda x: x.round_result[1])

        else:
            break
        
    hand_name = game.match_ranking_to_hand(winner.round_result[0])

    await ctx.send(f"The winner of this round is {winner.user} with {hand_name}!")

    await ctx.invoke(bot.get_command("add_pot_to_winner"), winner=winner)

    await ctx.invoke(bot.get_command("reset"))




@bot.command()
async def add_pot_to_winner(ctx, winner):
    for player in game.players:
        game.pot += player.money_betted
        player.total_money -= player.money_betted
    winner.total_money += game.pot
    await ctx.send(f"{winner.user} won {game.pot} this round.")

@bot.command()
async def reset(ctx):
    game.deck = Deck()
    game.displayhand = []
    game.players_in_game = []
    game.players = []
    game.pot, game.current_bet = 0, 0
    for player in game.players:
        player.hand = []
        player.money_betted = 0
        player.round_result = None
    await ctx.send("The game has been reset.")

@bot.command()
async def in_game(ctx):
    await ctx.send(len(game.players_in_game))

@bot.command()
async def DM(ctx, user: discord.User):
    message = "DM Successful"
    await user.send(message)


bot.run(TOKEN)