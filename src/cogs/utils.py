from discord.ext import commands
from datetime import datetime, timedelta
import discord, os, asyncio, random


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Convenient solutions to inconvenient tech problems')
    async def bofh(self, ctx):
        # https://stackoverflow.com/questions/14924721/how-to-choose-a-random-line-from-a-text-file#14924739
        line_num = 0
        selected = ''
        with open('data/excuses.txt') as f:
            while 1:
                line = f.readline()
                if not line: break
                line_num += 1
                if random.uniform(0, line_num) < 1:
                    selected = line
        await ctx.send(selected.strip())

    @commands.command(brief='Information about the bot instance')
    async def info(self, ctx):
        commit = os.popen('git rev-parse --short HEAD').read().strip()
        embed = discord.Embed(
            title="Malcolm-Next",
            url="https://github.com/TheOtherUnknown/Malcolm-next")
        embed.add_field(name="Running commit", value=commit,
                        inline=False)  # What commit is running?
        embed.add_field(name="Server count",
                        value=(len(self.bot.guilds)),
                        inline=False)
        embed.add_field(name="Owner", value=self.bot.Owner, inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        brief=
        'Add yourself to the verified user role in the server, if you qualify')
    async def verify(self, ctx):
        joindate = ctx.author.joined_at
        if datetime.now() > (joindate + timedelta(days=1)):  # One day
            await ctx.author.add_roles(
                discord.utils.get(ctx.guild.roles, name='Verified'))
            await ctx.message.add_reaction('✅')  # Check mark
        else:  # You didn't meet the time :(
            await ctx.send(
                'You don\'t qualify to be verified yet! Check back 24 hours after you join.'
            )

    ### START MOD COMMANDS ###
    @commands.command(brief='Bans a user from the server', usage='@someone')
    @commands.has_permissions(ban_members=True)
    async def kb(self, ctx):
        user = ctx.message.mentions[0]  # Get the first mentioned user
        await ctx.guild.ban(user, reason=f"Banned via command by {ctx.author}")

    @commands.command(brief="Kicks a mentioned user from the server",
                      usage="@someone")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx):
        if ctx.message.mentions[0] is not None:
            user = ctx.message.mentions[0]
            await ctx.guild.kick(user,
                                 reason=f"Kicked via command by {ctx.author}")

    @commands.command(brief='Mass-deletes messages in the current channel',
                      usage='<NUMBER>')
    @commands.has_permissions(manage_messages=True)
    async def nuke(self, ctx, num):
        if num is not None:
            num = int(
                num
            )  # Num can't be >100. That needs to be checked at some point
            async for message in ctx.channel.history(limit=num):
                message.delete()
            await asyncio.sleep(
                1.2)  # Sleep for a bit so everything gets deleted on time

    ### START OWNER COMMANDS ###
    @commands.command(hidden=True)
    @commands.is_owner()
    async def quit(self, ctx):
        await ctx.send('Malcolm is going down NOW!')
        raise SystemExit
