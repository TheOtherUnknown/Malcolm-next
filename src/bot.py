#!/usr/bin/env python3
from nextcord.ext import commands
import yaml, nextcord, sys, sqlite3, logging

from cogs.joinleave import JoinLeave
from cogs.roles import Roles
from cogs.utils import Utils
from cogs.trivia import Trivia
from cogs.admin import Admin
from core.malcomhelp import MalcolmHelp

class Malcolm(commands.Bot):
    """An extension of discord.ext.commands.Bot with configuration
    management and database management"""
    def __init__(self,
                 command_prefix,
                 configpath: str,
                 description=None,
                 **options):
        self.configpath = configpath
        conf_file = open(configpath)
        self.config = yaml.safe_load(conf_file)
        super().__init__(command_prefix,
                         description=description,
                         **options)

    def getConfig(self, section: str, item: str) -> str:
        """Returns a String value from the bot's config file"""
        if item == 'token':
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
            yaml.dump(self.config, configfile)

    def run(self):
        """Calls discord.ext.commands.Bot.run() with token info"""
        super().run(self.config['API']['token'])


intents = nextcord.Intents()
intents.members = True  # Join/Leave messages
intents.guild_messages = True  # Trivia
intents.bans = True  # Ban messages
intents.guilds = True  # Docs says so
intents.guild_reactions = True  # For roles

db = sqlite3.connect('data/malcolm.db')
cur = db.cursor()

logging.basicConfig(level=logging.WARN)
bot = Malcolm(command_prefix=',', intents=intents, configpath=sys.argv[1])


@bot.event
async def on_ready():
    logging.info('Malcolm-next has started')


bot.add_cog(JoinLeave(bot))
bot.add_cog(Trivia(bot, db, cur))
bot.add_cog(Utils(bot))
bot.add_cog(Roles(bot, db, cur))
bot.add_cog(Admin(bot))

bot.help_command = MalcolmHelp()

bot.run()
