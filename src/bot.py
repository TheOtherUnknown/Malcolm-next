#!/usr/bin/env python3
from discord.ext import commands
import configparser, discord, sys

from cogs.joinleave import JoinLeave
from cogs.utils import Utils
from cogs.trivia import Trivia

intents = discord.Intents()
intents.members = True  # Join/Leave messages
intents.guild_messages = True  # Trivia
intents.bans = True  # Ban messages
intents.guilds = True  # Docs says so

bot = commands.Bot(command_prefix=',', intents=intents)

config = configparser.ConfigParser()
try:
    config.read(sys.argv[1])
except (IndexError, IOError):
    print('Failed to read config file!')


@bot.event
async def on_ready():
    print('Malcolm-next has started')
    print('Invite URL here')


bot.add_cog(JoinLeave(bot))
bot.add_cog(Trivia(bot))
bot.add_cog(Utils(bot))

bot.owner_id = config['API']['OwnerID']
bot.run(config['API']['Token'])
