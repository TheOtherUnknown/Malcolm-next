from typing import Tuple
from discord.ext import commands
import discord
from asyncio import sleep, TimeoutError
from collections import Counter
from Levenshtein import ratio

locked_channels = []  # Channel IDs that are currently in use by a game


class Trivia(commands.Cog):
    def __init__(self, bot, db, cur):
        self.bot = bot
        self.db = db
        self.cur = cur

    # Helper methods
    def check_winner(self, scores: Counter, goal):
        """Is there a player in scores counter with a score of goal? If so,
        return a tuple. Else None"""
        for player, score in scores.items():
            if score == goal:
                del scores[player]
                return (player, (scores.elements()))  # Return (winner, (losers))
        return None  # Or none

    def get_dist(self, a: str, b: str) -> float:
        """Get a float between 0-1 indicating the similarity of two strings"""
        return ratio(a, b)

    def get_question(self) -> Tuple[str, str]:
        """Get one random (question, answer) from db"""
        return self.cur.execute(
            'SELECT question, answer FROM trivia ORDER BY Random() LIMIT 1'
        ).fetchone()

    def tally_scores(
            self, results: Tuple[discord.User, Tuple[discord.User,
                                                     ...]]) -> None:
        """Takes a tuple in the format (winner, (loser, loser)) and does the
        needful in the DB"""
        self.cur.execute(
            'INSERT INTO score(id, rank) VALUES (?, 1) ON CONFLICT(id) DO UPDATE SET rank=rank+1',
            (results[0], ))
        for loser in results[1]:
            self.cur.execute(
                'INSERT INTO score(id, losses) VALUES (?, 1) ON CONFLICT(id) DO UPDATE SET losses=losses+1',
                (loser, ))
        self.db.commit()

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
            scores = Counter()

            def check(message) -> bool:
                """Predicate function for bot.wait_for().
                Is the channel sent == the context channel and not the bot?"""
                return message.channel == ctx.channel and message.author != self.bot.user

            while play:  # TODO: Change this to True and use break/return
                question = self.get_question()
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
                # This line uses a fuzzy-match algorithm defined in get_ratio
                # to check if the input answer is *close* to the correct one.
                if self.get_dist(resp.content, question[1]) > .86:
                    await ctx.send('You got it!')
                    scores[resp.author.id] += 1
                else:  # Someone got the question wrong
                    await ctx.send('Nope! The correct answer was {}'.format(
                        question[1]))
                    # Even if they miss it, losses needed to be counted
                    if resp.author.id not in scores.keys():
                        scores[resp.author.id] = 0
                round_result = self.check_winner(scores, goal)
                if round_result is not None:
                    play = False
                    self.tally_scores(round_result)
                    await ctx.send(str(resp.author) + ' Wins!')
                    locked_channels.remove(ctx.channel.id)

    @trivia.command()
    async def top(self, ctx):
        """Sends an embed with the top 5 ranked users in trivia"""
        embed = discord.Embed(title="Trivia Leaderboard")
        i = 1
        for leader in self.cur.execute(
                'SELECT id, rank, losses FROM score ORDER BY rank DESC LIMIT 5'
        ):
            embed.add_field(name=f"{i}. {self.bot.get_user(leader[0]).name}",
                            value=f"{leader[1]} wins, {leader[2]} losses",
                            inline=False)
            i += 1
        await ctx.send(embed=embed)

    @trivia.command()
    async def stats(self, ctx):
        """Returns your trivia win/loss statistics"""
        embed = discord.Embed(title=f"{ctx.author.name}'s trivia stats")
        stats = self.cur.execute('SELECT rank, losses FROM score WHERE id = ?',
                                 (ctx.author.id, )).fetchone()
        if stats is None:
            await ctx.send(
                "Hmm, can't find any stats for you. Try playing at least one game."
            )
            return
        embed.add_field(name="Wins", value=stats[0])
        embed.add_field(name="Losses", value=stats[1])
        embed.add_field(name="Win ratio",
                        value="{:.2%}".format(stats[0] /
                                              (stats[0] + stats[1])),
                        inline=True)
        await ctx.send(embed=embed)

    @commands.command(usage="Phrase 1|Phrase 2")
    async def dist(self, ctx, *, arg):
        """Returns the distance of similarity between two strings seperated by a
        pipe |"""
        items = arg.split('|')
        await ctx.send(round(self.get_dist(items[0], items[1]), 2))
