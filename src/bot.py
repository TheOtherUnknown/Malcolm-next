#!/usr/bin/env python3
from discord.ext import commands
import configparser

bot = commands.Bot(command_prefix=',')

config = configparser.ConfigParser()
config.read('../config.ini')

@bot.event
async def on_ready():
    print('Malcolm-next has started')
    print('Invite URL here')

bot.owner_id = config['API']['OwnerID']
bot.run(config['API']['Token'])