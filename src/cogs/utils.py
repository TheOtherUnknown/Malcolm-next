from discord.ext import commands
from datetime import datetime, timedelta
import discord

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command()
    async def verify(self, ctx):
        joindate = ctx.author.joined_at
        if datetime.now() > (joindate + timedelta(days=1))  : # One day
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Verified'))
            await ctx.message.add_reaction('✅') # Check mark
        else:
            await ctx.send('You don\'t qualify to be verified yet! Check back 24 hours after you join.')

