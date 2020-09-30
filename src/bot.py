#!/usr/bin/env python3
from discord.ext import commands
import configparser

from cogs.joinleave import JoinLeave

bot = commands.Bot(command_prefix=',')

config = configparser.ConfigParser()
config.read('../config.ini')


@bot.event
async def on_ready():
    print('Malcolm-next has started')
    print('Invite URL here')


bot.add_cog(JoinLeave(bot))
# bot.add_cog(Trivia(bot))

bot.owner_id = config['API']['OwnerID']
bot.run(config['API']['Token'])