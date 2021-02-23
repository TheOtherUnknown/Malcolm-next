import discord, os, asyncio, random
from discord.ext import commands
from datetime import datetime, timedelta, date
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
        """The time it takes for disords servers to respond to Malcolm"""
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
        brief='Convert time from one timezone to another',
        usage='[time] [original timezone] [timezone to convert too]')
    async def time(self, ctx, times, period, og_tz, new_tz):
        """
        Convert time from one timezone to another
        """

        formate = "%I:%M:%S %p"

        h, m = times.split(
            ':')  # Get the hour and minutes from the provided time
        y, m_, d = str(date.today()).split(
            '-'
        )  # Get the year, month, and date for use in the datetime.datetime object

        # Make the timezones uppercase for use in the convert_tz function
        try:
            og_tz = og_tz.upper()
            new_tz = new_tz.upper()

            def convert_tz(timezone):
                # Convert the user given timezone into a valid pytz timezone
                if timezone == 'EST':
                    timezone = 'America/New_York'
                elif timezone == 'CET':
                    timezone = 'Europe/London'
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
                    timezone = 'America/Nome'
                elif timezone == 'MST':
                    timezone = 'America/Los_Angeles'
                elif timezone == 'CST':
                    timezone = 'America/Denver'
                elif timezone == 'AST':
                    timezone = 'America/Aruba'
                elif timezone == 'ART':
                    timezone = 'America/Belem'
                elif timezone == 'AT':
                    timezone = 'America/Godthab'
                elif timezone == 'WAT':
                    timezone = 'Atlantic/Cape_Verde'
                elif timezone == 'GMT' or timezone == 'UTC':
                    timezone = 'Universal'

                return timezone

            # If the user is passing in PM as an arugment then convert it to 24hr format by adding 12 to it
            # If the user is passing in AM as an arugment do nothing as it would already be in 12hr format
            if period.lower() == 'pm':
                h = int(h) + 12

            # Use the function on the user provided timezones
            og_tzs = convert_tz(og_tz)
            new_tzs = convert_tz(new_tz)

            # Get the current time and date (We do this because you cannot call `.astimezone()` on datetime.time)
            local = datetime(int(y), int(m_), int(d), int(h), int(m))

            # Take the current time and make change it into the original timezone, then convert it to the new timezone
            non_local = pytz.timezone(og_tzs).localize(local).astimezone(
                pytz.timezone(new_tzs))

            # Apply formatting to our times so we dont get the date and milliseconds
            non_local = non_local.strftime(formate)
            local = local.strftime(formate)

            await ctx.send(
                f"{local} in {og_tz}({og_tzs}) is {non_local} in {new_tz}({new_tzs})"
            )
        except Exception:
            await ctx.send('Sorry didn\'t understand that. For formatting see `,help time`')

    # == START MOD COMMANDS == #
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
