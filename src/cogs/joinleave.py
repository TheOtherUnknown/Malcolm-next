import random
from discord.ext import commands
join_msgs = ('Leave your weapons at the door.', 'We just ran out of coffee.',
             "You'll have to be better than that to not be spotted.",
             "Trust the cloak.", "One riot. One Ranger.",
             "Gorlog's breath, another one?",
             "I'm a King's Ranger, as you've probably guessed.",
             "Everyone stay down. I'm going to ram.")


class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(
                f'{member.mention} has joined. {random.choice(join_msgs)}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'{member} has left the server')
