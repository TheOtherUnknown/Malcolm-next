import discord, os, asyncio, random
from discord.ext import commands
from datetime import datetime, timedelta
import pytz


# Helper methods
# Gets the user's roles, converts them to strings, and makes a comma seperated list out of them.
# Ignore @everyone if they have other roles
def role_list(user):
    roles = list(map(str, user.roles))
    if len(roles) != 1:
        roles.remove('@everyone')
    return ', '.join(roles)


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
                if not line:
                    break
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
        embed.add_field(name="Running Commit", value=commit,
                        inline=False)  # What commit is running?
        embed.add_field(name="Server count",
                        value=(len(self.bot.guilds)),
                        inline=False)
        embed.add_field(name="Owner", value=self.bot.owner_id, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Displays latency between client and bot"""
        latency = round(self.bot.latency * 1000, 2)
        return await ctx.send('Pong! ' + str(latency) + 'ms')

    @commands.command()
    async def roll(self, ctx, roll='1d6'):
        """Rolls a dice"""
        embed = discord.Embed(title='Dice Rolls')
        try:
            sides = int(roll.split('d')[1])
            rolls = int(roll.split('d')[0])
        except Exception:
            await ctx.send(
                'Wrong format, the commands format is `[number of rolls]d[number of sides]` eg.(1d5, or 10d45)'
            )
            return

        if sides < 1:
            sides = 1
        elif sides > 1000000000000:
            sides = 1000000000000

        if rolls < 1:
            rolls = 1
        elif rolls > 100:
            rolls = 100

        total = 0

        for x in range(rolls):
            val = random.randint(1, sides)
            total += val
            embed.add_field(name=f"Dice  #{x + 1}", value=val)
        embed.set_footer(text=f"Total: {total}")
        await ctx.send(embed=embed)

    @commands.command(brief='Displays information about the server')
    async def serverinfo(self, ctx):
        embed = discord.Embed(title=ctx.guild.name)
        if ctx.guild.description is not None:
            embed.description = ctx.guild.description
        embed.add_field(name='Region',
                        value=str(ctx.guild.region),
                        inline=True)
        embed.add_field(name='Members',
                        value=str(ctx.guild.member_count),
                        inline=True)
        embed.add_field(name='Owner', value=ctx.guild.owner.name, inline=True)
        cdate = ctx.guild.created_at
        embed.add_field(
            name='Creation date',
            value=f"{cdate.ctime()}, {(datetime.utcnow() - cdate).days} days ago")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        await ctx.send(embed=embed)

    @commands.command(brief='Displays information about users')
    async def userinfo(self, ctx, userid=None):
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif userid:
            user = ctx.guild.get_member(int(userid))
            if not user:
                await ctx.send("Cannot find user with that ID!")
                return
        else:
            user = ctx.author
        embed = discord.Embed(title=str(user))
        embed.set_thumbnail(url=user.avatar_url)
        create = f"{user.created_at.ctime()}, {(datetime.utcnow() - user.created_at).days} days ago"
        embed.add_field(name='Account created', value=create, inline=False)
        join = f"{user.joined_at.ctime()}, {(datetime.utcnow() - user.joined_at).days} days ago"
        embed.add_field(name="Join date", value=join, inline=False)
        embed.add_field(name="Roles", value=role_list(user), inline=False)
        embed.set_footer(text=f"ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command(
        brief='Add yourself to the verified user role in the server, if you qualify')
    async def verify(self, ctx):
        joindate = ctx.author.joined_at
        if datetime.utcnow() > (joindate + timedelta(days=1)):  # One day
            await ctx.author.add_roles(
                discord.utils.get(ctx.guild.roles, name='Verified'))
            await ctx.message.add_reaction('✅')  # Check mark
        else:  # You didn't meet the time :(
            await ctx.send(
                'You don\'t qualify to be verified yet! Check back 24 hours after you join.'
            )

    @commands.command(
        usage="[time] [am/pm] [original timezone] [timezone to convert to]")
    async def time(self, ctx, utime, apm, ozone, nzone):
        """Converts times from one timezone to another"""
        tformat = '%I:%M %p'

        def convert_tz(timezone: str):
            # Convert the user given timezone into a valid pytz timezone
            timezone = timezone.upper()
            if timezone == 'EST':
                timezone = 'America/New_York'
            elif timezone == 'CET':
                timezone = 'Europe/Paris'
            elif timezone == 'EET':
                timezone = 'Europe/Amsterdam'
            elif timezone == 'MSK':
                timezone = 'Europe/Moscow'
            elif timezone == 'AMT':
                timezone = 'Asia/Dubai'
            elif timezone == 'PKT':
                timezone = 'Indian/Maldives'
            elif timezone == 'OMSK':
                timezone = 'Indian/Chagos'
            elif timezone == 'KRAT':
                timezone = 'Asia/Bangkok'
            elif timezone == 'JST':
                timezone = 'Asia/Tokyo'
            elif timezone == 'AEST':
                timezone = 'Australia/Queensland'
            elif timezone == 'SAKT':
                timezone = 'Pacific/Ponape'
            elif timezone == 'NZST':
                timezone = 'Pacific/Fiji'
            elif timezone == 'IDLW':
                timezone = 'Etc/GMT+12'
            elif timezone == 'NT':
                timezone = 'US/Samoa'
            elif timezone == 'HST':
                timezone = 'Pacific/Honolulu'
            elif timezone == 'AKST':
                timezone = 'America/Adak'
            elif timezone == 'PST':
                timezone = 'America/Phoenix'
            elif timezone == 'MST':
                timezone = 'America/Denver'
            elif timezone == 'CST':
                timezone = 'America/Chicago'
            elif timezone == 'AST':
                timezone = 'America/Aruba'
            elif timezone == 'ART':
                timezone = 'America/Belem'
            elif timezone == 'AT':
                timezone = 'America/Godthab'
            elif timezone == 'WAT':
                timezone = 'Atlantic/Cape_Verde'
            else:
                timezone = 'Universal'

            return pytz.timezone(timezone)

        nzone = convert_tz(nzone)
        ozone = convert_tz(ozone)
        try:
            # This should make us DST aware... Maybe
            utime = datetime.strptime(f"{utime} {apm}", tformat)
            utime = ozone.localize(
                datetime.combine(date=datetime.today(), time=utime.time()))
        except ValueError:
            await ctx.send('Couldn\'t parse that time, see ,help time')
            return

        otime = datetime.strftime(utime, tformat)
        ntime = datetime.strftime(utime.astimezone(nzone), tformat)
        await ctx.send(f"{otime} {ozone} is {ntime} {nzone}")

    # == START MOD COMMANDS == #

    @commands.command(brief='Create polls using embeds and reactions',
                      usage="\"question\" \"answers 1-9\"")
    @commands.has_any_role(
        'Mods', 616448412057075768
    )  # Only people with the role of Mods can use this command
    async def poll(self, ctx, question, *args):
        """
        Create embed polls with one question and up to 9 responses.
        """
        # Curernt max amount of answers is 9 as there are only 9 digit reactions

        if len(args) > 9:
            return await ctx.send(
                "You have provided more than nine choices; therefore, the poll was not sent"
            )

        reactions = [
            '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣'
        ]  # A list of all the reactions that could be added

        user = ctx.author  # Get the author for the footer of the embed

        embed = discord.Embed(
            title=f"**__{question}__**"
        )  # Set the title of the embed as the question provided
        embed.set_thumbnail(
            url=user.avatar_url
        )  # Set the thumbnail as the authors discord profile picture
        embed.set_author(
            name=user
        )  # Set the author of the embed as the person who sent the command

        for i, j in enumerate(args, 1):
            embed.add_field(name=str(i), value=str(j))

        msg = await ctx.send(embed=embed)

        for x in range(len(args)):
            await msg.add_reaction(reactions[x])

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

    # == START OWNER COMMANDS == #
    @commands.command(hidden=True)
    @commands.is_owner()
    async def quit(self, ctx):
        await ctx.send('Malcolm is going down NOW!')
        raise SystemExit
