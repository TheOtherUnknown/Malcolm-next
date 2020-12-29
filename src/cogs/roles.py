from discord.ext import commands
import sqlite3

db = sqlite3.connect('data/malcolm.db')
cur = db.cursor()


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rolechan(self, ctx):
        chan = ctx.message.channel_mentions[0]
        if chan.id == self.bot.getConfig('Roles', 'Channel'):
            return
        self.bot.setConfig('Roles', 'Channel', str(chan.id))
