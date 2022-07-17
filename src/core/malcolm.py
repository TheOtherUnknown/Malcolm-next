from nextcord.ext import commands
import yaml


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
                         help_command=None,
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
