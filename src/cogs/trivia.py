from typing import Tuple, Dict
from nextcord.ext import commands, application_checks
import nextcord, sqlite3
from asyncio import sleep, TimeoutError
from Levenshtein import ratio

locked_channels = []  # Channel IDs that are currently in use by a game


class Trivia(commands.Cog):

    def __init__(self, bot, db, cur):
        self.bot = bot
        self.db = db
        self.cur = cur
        self.last_add = None  # The last question that was added via trivia add

    # Helper methods
    # Dict[int,int] Is replaced in 3.8
    def check_winner(self, scores: Dict[int, int], goal):
        """Is there a player in scores dict with a score of goal? If so,
        return a tuple. Else None"""
        for player, score in scores.items():
            if score == goal:
                del scores[player]
                return (player, (scores.keys()))  # Return (winner, (losers))
        return None  # Or none

    def get_dist(self, a: str, b: str) -> float:
        """Get a float between 0-1 indicating the similarity of two strings,
        case insensitive"""
        return ratio(a.lower(), b.lower())

    def get_question(self) -> Tuple[str, str]:
        """Get one random (question, answer) from db"""
        return self.cur.execute(
            'SELECT question, answer FROM trivia ORDER BY Random() LIMIT 1'
        ).fetchone()

    def tally_scores(
            self, results: Tuple[nextcord.User, Tuple[nextcord.User,
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

    @nextcord.slash_command()
    async def trivia(self, _inter: nextcord.Interaction):
        """An RA themed competitive trivia game, with scoreboard"""
        pass

    @trivia.subcommand()
    async def start(self,
                    inter: nextcord.Interaction,
                    goal: int = nextcord.SlashOption(
                        description='Number of questions to ask',
                        min_value=5,
                        max_value=50,
                        default=5)):
        """Starts a new trivia game in the current channel"""

        questions = set()  # Questions that have been sent

        if inter.channel_id not in locked_channels:
            locked_channels.append(inter.channel_id)
            await inter.send(
                f'Starting trivia. The first to {goal} points wins!')
            play = True
            scores = {}

            def check(message) -> bool:
                """Predicate function for bot.wait_for().
                Is the channel sent == the context channel and not the bot?"""
                return message.channel.id == inter.channel_id and message.author != self.bot.user

            while play:  # TODO: Change this to True and use break/return
                question = self.get_question()
                if question not in questions:  # If the sent question was not already sent (no in the list questions) proceed as normal
                    await sleep(2)
                    await inter.send(question[0])
                    try:
                        resp = await self.bot.wait_for(
                            'message', check=check,
                            timeout=60.0)  # Wait 60secs for an answer
                    except TimeoutError:
                        locked_channels.remove(inter.channel_id)
                        await inter.send('Alright then, exiting...'
                                         )  # No answer? Then stop the game
                        break
                    if resp.content == "stop":  # The answer is 'stop'? End the game
                        await inter.send('Exiting...')
                        locked_channels.remove(inter.channel_id)
                        break
                    # This line uses a fuzzy-match algorithm defined in get_ratio
                    # to check if the input answer is *close* to the correct one.
                    if self.get_dist(resp.content, question[1]) > .86:
                        await inter.send('You got it!')
                        # Prevent a KeyError by making sure the user is in the dict
                        if resp.author.id in scores:
                            scores[resp.author.id] += 1
                        else:
                            scores[resp.author.id] = 1
                    else:  # Someone got the question wrong
                        await inter.send(
                            f'Nope! The correct answer was {question[1]}')
                        # Even if they miss it, losses needed to be counted
                        if resp.author.id not in scores.keys():
                            scores[resp.author.id] = 0
                    round_result = self.check_winner(scores, goal)
                    if round_result is not None:
                        play = False
                        self.tally_scores(round_result)
                        await inter.send(str(resp.author) + ' Wins!')
                        locked_channels.remove(inter.channel_id)
                    questions.add(question)
                else:
                    if len(
                            questions
                    ) > 100:  # If the question has been sent just check to see that the list isn't too big
                        questions = set()  # If it is, clean the set

    @trivia.subcommand()
    async def top(self, inter: nextcord.Interaction):
        """Sends an embed with the top 5 ranked users in trivia"""
        embed = nextcord.Embed(title="Trivia Leaderboard")
        last = {
        }  # Declare a dictionary in function scope to hold the amount of wins and losses of the last person checked
        i = 0
        for leader in self.cur.execute(
                'SELECT id, rank, losses FROM score ORDER BY rank DESC, losses ASC LIMIT 5'  # Sort by both rank and losses. If the ranks are equal then the person with less losses should be ranked higher
        ):
            if leader[1] != last.get('rank') or leader[2] != last.get(
                    'losses'
            ):  # If the wins and losses are not equal to the last person checked then the place number should increase
                i += 1

            embed.add_field(name=f"{i}. {self.bot.get_user(leader[0]).name}",
                            value=f"{leader[1]} wins, {leader[2]} losses",
                            inline=False)

            last = {
                'rank': leader[1],
                'losses': leader[2]
            }  # While still in the current iteration assign the last variable
        await inter.send(embed=embed)

    @trivia.subcommand()
    async def stats(self, inter: nextcord.Interaction):
        """Returns your trivia win/loss statistics"""
        embed = nextcord.Embed(title=f"{inter.user.name}'s trivia stats")
        stats = self.cur.execute('SELECT rank, losses FROM score WHERE id = ?',
                                 (inter.user.id, )).fetchone()
        if stats is None:
            await inter.send(
                "Hmm, can't find any stats for you. Try playing at least one game."
            )
            return
        embed.add_field(name="Wins", value=stats[0])
        embed.add_field(name="Losses", value=stats[1])
        embed.add_field(name="Win ratio",
                        value="{:.2%}".format(stats[0] /
                                              (stats[0] + stats[1])),
                        inline=True)
        await inter.send(embed=embed)

    @trivia.subcommand()
    async def add(self, inter: nextcord.Interaction):
        """Adds a new question to the database"""
        senderscore = self.cur.execute('SELECT rank FROM score WHERE id = ?',
                                       (inter.user.id, )).fetchone()

        def check(message: nextcord.Message) -> bool:
            """Predicate function to ensure the same user responds
            in the same channel"""
            return message.channel.id == inter.channel_id and inter.user == message.author

        if senderscore is not None and senderscore[0] > 24:
            try:
                await inter.send('Enter the question to add: ')
                question = await self.bot.wait_for('message',
                                                   check=check,
                                                   timeout=60.0)
                await inter.send('Enter the answer: ')
                answer = await self.bot.wait_for('message',
                                                 check=check,
                                                 timeout=60.0)
            except TimeoutError:
                await inter.send('Timed out, quitting...')
                return
            try:
                self.cur.execute('INSERT INTO trivia VALUES(?,?,?)',
                                 (question.clean_content, answer.clean_content,
                                  inter.user.id))
                self.db.commit()
            except sqlite3.IntegrityError:
                # UNIQUE contraint violated or other problem
                await inter.send(
                    'That question is too similar to another, try something else'
                )
                self.db.rollback()
            # We added a question! Send success message
            await inter.send('Question was added!')
            self.last_add = question.clean_content
        else:
            # We don't meet the precondition, send an error
            await inter.send(
                'You need at least 25 trivia wins to add questions, try again later!'
            )

    @trivia.subcommand()
    @application_checks.has_permissions(manage_messages=True)
    async def undo(self, inter: nextcord.Interaction):
        """Removes the last added question"""
        if self.last_add is None:
            await inter.send('No questions to be removed')
            return
        self.cur.execute('DELETE FROM trivia WHERE question=?',
                         (self.last_add, ))
        self.db.commit()
        self.last_add = None
        await inter.send('Last question was removed')
