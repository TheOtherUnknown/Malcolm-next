#!/usr/bin/env python3
from core.malcolm import Malcolm
import nextcord, sys, sqlite3, logging

from cogs.joinleave import JoinLeave
from cogs.roles import Roles
from cogs.utils import Utils
from cogs.fun import Fun
from cogs.trivia import Trivia
from cogs.admin import Admin

intents = nextcord.Intents()
intents.members = True  # Join/Leave messages
intents.guild_messages = True  # Trivia
intents.bans = True  # Ban messages
intents.guilds = True  # Docs says so
intents.guild_reactions = True  # For roles
intents.message_content = True  # Needed for commands now :(

db = sqlite3.connect('data/malcolm.db')
cur = db.cursor()

logging.basicConfig(level=logging.WARN)
bot = Malcolm(intents=intents, configpath=sys.argv[1])


@bot.event
async def on_ready():
    logging.info('Malcolm-next has started')


bot.add_cog(JoinLeave(bot))
bot.add_cog(Trivia(bot, db, cur))
bot.add_cog(Utils(bot))
bot.add_cog(Roles(bot, db, cur))
bot.add_cog(Admin(bot))
bot.add_cog(Fun(bot))

bot.run()
