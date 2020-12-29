#!/usr/bin/env python3
from discord.ext import commands
import configparser, discord, sys

from cogs.joinleave import JoinLeave
from cogs.roles import Roles
from cogs.utils import Utils
from cogs.trivia import Trivia


class Malcolm(commands.Bot):
    """An extension of discord.ext.commands.Bot with configuration
    management"""
    def __init__(self,
                 command_prefix,
                 configpath: str,
                 help_command=commands.DefaultHelpCommand(),
                 description=None,
                 **options):
        self.configpath = configpath
        self.config = configparser.ConfigParser()
        self.config.read(configpath)
        super().__init__(command_prefix,
                         help_command=help_command,
                         description=description,
                         **options)

    def getConfig(self, section: str, item: str) -> str:
        """Returns a String value from the bot's config file"""
        if item == 'Token':
            # Yes, I'm aware that the original ConfigParser is avalible.
            # This is more of a reminder for me
            raise PermissionError('You can\'t get the token during runtime')
        return self.config[section][item]

    def setConfig(self, section: str, item: str, value: str) -> None:
        """Changes a configuration value, and writes it to the file"""
        if section == "API":
            # Yes, I'm aware that the original ConfigParser is avalible.
            # This is more of a reminder for me
            raise PermissionError(
                "You can't modify API settings while the bot is running!")
        self.config[section][item] = value
        with open(self.configpath, 'w') as configfile:
            self.config.write(configfile)

    def run(self):
        """Calls discord.ext.commands.Bot.run() with token info"""
        super().run(self.config['API']['Token'])


intents = discord.Intents()
intents.members = True  # Join/Leave messages
intents.guild_messages = True  # Trivia
intents.bans = True  # Ban messages
intents.guilds = True  # Docs says so

bot = Malcolm(command_prefix=',', intents=intents, configpath=sys.argv[1])


@bot.event
async def on_ready():
    print('Malcolm-next has started')
    print('Invite URL here')


bot.add_cog(JoinLeave(bot))
bot.add_cog(Trivia(bot))
bot.add_cog(Utils(bot))
bot.add_cog(Roles(bot))

bot.run()
