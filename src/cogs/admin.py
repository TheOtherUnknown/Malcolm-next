from nextcord.ext import commands, application_checks
import nextcord, asyncio


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(dm_permission=False)
    @application_checks.has_permissions(manage_messages=True)
    async def nuke(self,
                   inter: nextcord.Interaction,
                   num: int = nextcord.SlashOption(
                       required=True,
                       min_value=5,
                       max_value=200,
                       description='Number of messages to delete')):
        """Mass-deletes messages in the current channel"""
        # Num can't be >100. That needs to be checked at some point
        async for message in inter.channel.history(limit=num):
            await message.delete()
        await asyncio.sleep(
            1.2)  # Sleep for a bit so everything gets deleted on time

    # == START OWNER COMMANDS == #
    @nextcord.slash_command()
    @application_checks.is_owner()
    async def quit(self, inter: nextcord.Interaction):
        await inter.send('Malcolm is going down NOW!')
        raise SystemExit
