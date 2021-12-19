import nextcord
from nextcord.ext import commands


class MalcolmHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = nextcord.Embed(description=page)
            await destination.send(embed=emby)