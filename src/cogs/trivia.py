from discord.ext import commands
import sqlite3, discord
from asyncio import sleep

db = sqlite3.connect('data/trivia.db')
cur = db.cursor()
locked_channels = []  # Channel IDs that are currently in use by a game


# Helper methods
# Get one random (question, answer) from db
def get_question():
    return cur.execute(
        'SELECT question, answer FROM trivia ORDER BY Random() LIMIT 1'
    ).fetchone()


def check_winner(scores, goal):
    # Is there a player in scores dict with a score of goal? If so, return a tuple. Else None
    for player in scores:
        if scores[player] == goal:
            scores.pop(player)
            return (player, (scores.keys()))  # Return (winner, (losers))
        return None  # Or none


# Takes a tuple in the format (winner, (loser, loser)) and does the needful in the DB
def tally_scores(results):
    cur.execute('UPDATE score SET rank = rank + 1 WHERE id = ?', results[0])
    for loser in results[1]:
        cur.execute('UPDATE score SET losses = losses + 1 WHERE id = ?', loser)
    db.commit()


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
        """Starts a new trivia game in the current channel"""
        # Ensure someone is not trying to start two games in the same channel
        if ctx.channel.id not in locked_channels:
            locked_channels.append(ctx.channel.id)
            await ctx.send(
                'Starting trivia. The first to {} points wins!'.format(goal))
            play = True
            scores = {}

            def check(message):
                # Predicate function for bot.wait_for(). Is the channel sent == the context channel?
                return message.channel == ctx.channel

            while play:
                question = get_question()
                await sleep(2)
                await ctx.send(question[0])
                try:
                    resp = await self.bot.wait_for(
                        'message', check=check,
                        timeout=60.0)  # Wait 60secs for an answer
                except TimeoutError:
                    locked_channels.remove(ctx.channel.id)
                    await ctx.send('Alright then, exiting...'
                                   )  # No answer? Then stop the game
                    break
                if resp.content == "stop":  # The answer is 'stop'? End the game
                    await ctx.send('Exiting...')
                    locked_channels.remove(ctx.channel.id)
                    break
                if resp.content == question[
                        1]:  # Someone got the question right
                    await ctx.send('You got it!')
                    scores[resp.author.id] += 1
                else:  # Somone got the question wrong
                    await ctx.send('Nope! The correct answer was {}'.format(
                        question[1]))
                    # Even if they miss it, losses needed to be counted
                    if resp.author.id not in scores.keys():
                        scores[resp.author.id] = 0
                round_result = check_winner(scores, goal)
                if round_result is not None:
                    play = False
                    tally_scores(round_result)
                    await ctx.send(str(resp.author) + ' Wins!')

    @trivia.command()
    async def top(self, ctx):
        """Sends an embed with the top 5 ranked users in trivia"""
        embed = discord.Embed(title="Trivia Leaderbord")
        for leader in cur.execute(
                'SELECT id, rank FROM score ORDER BY rank DESC LIMIT 5'):
            embed.add_field(name=self.bot.get_user(leader[0]),
                            value=f"Wins: {leader[1]}",
                            inline=False)
        await ctx.send(embed=embed)
