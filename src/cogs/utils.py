import nextcord, os
from nextcord.ext import commands
from datetime import datetime, timedelta
import zoneinfo


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
        self.UTC = zoneinfo.ZoneInfo('UTC')

    @commands.command(help='Information about the bot instance')
    async def info(self, ctx):
        commit = os.popen('git rev-parse --short HEAD').read().strip()
        embed = nextcord.Embed(
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

    @commands.command(help='Displays information about the server')
    async def serverinfo(self, ctx):
        embed = nextcord.Embed(title=ctx.guild.name)
        if ctx.guild.description is not None:
            embed.description = ctx.guild.description
        embed.add_field(name='Members',
                        value=str(ctx.guild.member_count),
                        inline=True)
        embed.add_field(name='Owner', value=ctx.guild.owner.name, inline=True)
        cdate = ctx.guild.created_at
        embed.add_field(
            name='Creation date',
            value=f"{cdate.ctime()}, {(datetime.now(self.UTC) - cdate).days} days ago"
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        await ctx.send(embed=embed)

    @commands.command(help='Displays information about users')
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
        embed = nextcord.Embed(title=str(user))
        embed.set_thumbnail(url=user.display_avatar.url)
        create = f"{user.created_at.ctime()}, {(datetime.now(self.UTC) - user.created_at).days} days ago"
        embed.add_field(name='Account created', value=create, inline=False)
        join = f"{user.joined_at.ctime()}, {(datetime.now(self.UTC) - user.joined_at).days} days ago"
        embed.add_field(name="Join date", value=join, inline=False)
        embed.add_field(name="Roles", value=role_list(user), inline=False)
        embed.set_footer(text=f"ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command(
        help='Add yourself to the verified user role in the server, if you qualify')
    async def verify(self, ctx):
        joindate = ctx.author.joined_at
        if datetime.now(self.UTC) > (joindate + timedelta(days=1)):  # One day
            await ctx.author.add_roles(
                nextcord.utils.get(ctx.guild.roles, name='Verified'))
            await ctx.message.add_reaction('✅')  # Check mark
        else:  # You didn't meet the time :(
            await ctx.send(
                'You don\'t qualify to be verified yet! Check back 24 hours after you join.'
            )

    @commands.command(
        usage="[time][am/pm] [original timezone] [timezone to convert to]")
    async def time(self, ctx, utime, ozone, nzone):
        """Converts times from one timezone to another. For a list of timezones see: https://github.com/TheOtherUnknown/Malcolm-next/wiki/Commands#time"""
        tformat = '%I:%M%p'

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
                timezone = 'America/Los_Angeles'
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

            return zoneinfo.ZoneInfo(timezone)

        nzone = convert_tz(nzone)
        ozone = convert_tz(ozone)
        try:
            utime = datetime.strptime(utime, tformat)
            utime = datetime.combine(date=datetime.today(), time=utime.time())
        except ValueError:
            await ctx.send('Couldn\'t parse that time, see `,help time`')
            return

        otime = datetime.strftime(utime, tformat)
        ntime = datetime.strftime(utime.astimezone(nzone), tformat)
        await ctx.send(f"{otime} {ozone} is {ntime} {nzone}")
