from discord.ext import commands
import discord, logging


def get_emoji(letter: str) -> str:
    """Return a letter emoji representing the given capital letter"""
    letter = ord(letter)
    # 127462 is the A emoji
    return chr(127462 + (letter - 65))


def get_letter(emoji: str) -> str:
    """Return a letter representing the given letter emoji"""
    emoji = ord(emoji)
    return chr(emoji - 127397)


class Roles(commands.Cog):
    def __init__(self, bot, db, cur):
        self.bot = bot
        self.db = db
        self.cur = cur

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def rolechan(self, ctx):
        chan = ctx.message.channel_mentions[0]
        if chan.id == self.bot.getConfig('Roles', 'Channel'):
            return
        self.bot.setConfig('Roles', 'Channel', str(chan.id))
        msg = 'React with one of the emotes below to be given the indicated vanity role:\n'
        for role in self.cur.execute('SELECT * from roles'):
            msg += f"* {role[1]} = {get_emoji(role[0])}\n"
        await ctx.send(msg)

    @commands.Cog.listener()
    async def on_reaction_add(self, react, user):
        chan_id = react.message.channel.id
        if chan_id == self.bot.getConfig(
                'Roles', 'Channel'
        ) and react.message.id == react.message.channel.last_message:
            entry = self.cur.execute('SELECT * FROM roles where letter=?',
                                     (get_letter(str(react), ))).fetchone()
            role = discord.utils.get(react.guild.roles, name=entry[1])
            if not role:
                logging.error(
                    'User attempted to add role %s which was not found, ignoring',
                    entry[1])
                return
            user.add_roles(role)
