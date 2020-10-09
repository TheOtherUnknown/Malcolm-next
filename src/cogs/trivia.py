from discord.ext import commands
import sqlite3
from time import sleep

db = sqlite3.connect('data/trivia.db')
cur = db.cursor()
locked_channels = []  # Channel IDs that are currently in use by a game


# Helper methods
def get_question():
    return cur.execute(
        'SELECT question, answer FROM trivia ORDER BY Random() LIMIT 1'
    ).fetchone()  # Get one random (question, answer) from db


def check_winner(scores, goal):
    for player in scores:
        if scores[player] == goal:
            scores.pop(player)
            return (player, (scores.keys()))  # Return (winner, (losers))
        return  # Or none


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        description='An RA themed competitive trivia game, with scoreboard.')
    async def trivia(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Trivia what? Use `,trivia start|top|stats`')

    @trivia.command()
    async def start(self, ctx, goal=5):
        if ctx.channel.id not in locked_channels:  # Is somone trying to start a second game in the same channel?
            locked_channels.append(ctx.channel.id)
            await ctx.send(
                'Starting trivia. The first to {} points wins!'.format(goal))
            play = True
            scores = {}

            def check(message):  # Predicate function for bot.wait_for()
                return message.channel == ctx.channel

            while play:
                question = get_question()
                sleep(3)
                await ctx.send(question[0])
                try:
                    resp = await self.bot.wait_for('message',
                                                   check=check,
                                                   timeout=60.0)
                except TimeoutError:
                    locked_channels.remove(ctx.channel.id)
                    await ctx.send('Alright then, exiting...')
                    break
                if resp.content == "stop":  # user wants to stop the game
                    await ctx.send('Exiting...')
                    locked_channels.remove(ctx.channel.id)
                    break
                elif resp.content == question[1]:
                    await ctx.send('You got it!')
                    scores[resp.author.id] += 1
                else:
                    await ctx.send('Nope! The correct answer was {}'.format(
                        question[1]))
                    if resp.author.id not in scores.keys():
                        scores[
                            resp.author.
                            id] = 0  # Even if they miss it, losses needed to be counted
                round_result = check_winner(scores, goal)
                if round_result is not None:
                    play = False
                    await ctx.send(str(resp.author) + ' Wins!')
