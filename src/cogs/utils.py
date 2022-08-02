import nextcord, os
from nextcord.ext import commands
from datetime import datetime, timedelta
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

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

    @nextcord.slash_command()
    async def info(self, inter: nextcord.Interaction):
        """Information about the bot instance"""
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
        await inter.send(embed=embed)

    @nextcord.slash_command()
    async def ping(self, inter: nextcord.Interaction):
        """Displays latency between client and bot"""
        latency = round(self.bot.latency * 1000, 2)
        return await inter.send('Pong! ' + str(latency) + 'ms')

    @nextcord.slash_command(dm_permission=False)
    async def serverinfo(self, inter: nextcord.Interaction):
        """Displays information about the server"""
        embed = nextcord.Embed(title=inter.guild.name)
        if inter.guild.description is not None:
            embed.description = inter.guild.description
        embed.add_field(name='Members',
                        value=str(inter.guild.member_count),
                        inline=True)
        embed.add_field(name='Owner',
                        value=inter.guild.owner.name,
                        inline=True)
        cdate = inter.guild.created_at
        embed.add_field(
            name='Creation date',
            value=f"{cdate.ctime()}, {(datetime.now(self.UTC) - cdate).days} days ago"
        )
        embed.set_thumbnail(url=inter.guild.icon.url)
        embed.set_footer(text=f"ID: {inter.guild.id}")
        await inter.send(embed=embed)

    @nextcord.slash_command(dm_permission=False)
    async def userinfo(self,
                       inter: nextcord.Interaction,
                       userid: nextcord.Member = nextcord.SlashOption(
                           description="ID or @user to check", default=None)):
        """Displays information about users"""
        if userid:
            # The library guarantees that if userid isn't none, it is a Member
            user = userid
        else:
            user = inter.user
        embed = nextcord.Embed(title=str(user))
        embed.set_thumbnail(url=user.display_avatar.url)
        create = f"{user.created_at.ctime()}, {(datetime.now(self.UTC) - user.created_at).days} days ago"
        embed.add_field(name='Account created', value=create, inline=False)
        join = f"{user.joined_at.ctime()}, {(datetime.now(self.UTC) - user.joined_at).days} days ago"
        embed.add_field(name="Join date", value=join, inline=False)
        embed.add_field(name="Roles", value=role_list(user), inline=False)
        embed.set_footer(text=f"ID: {user.id}")
        await inter.send(embed=embed)

    @nextcord.user_command(name='Show userinfo')
    async def userinfo_submenu(self, inter: nextcord.Interaction,
                               member: nextcord.Member):
        await self.userinfo(inter, member)

    @nextcord.slash_command()
    async def verify(self, inter: nextcord.Interaction):
        """Add yourself to the verified user role in the server, if you qualify"""
        joindate = inter.user.joined_at
        if datetime.now(self.UTC) > (joindate + timedelta(days=1)):  # One day
            await inter.user.add_roles(
                nextcord.utils.get(inter.guild.roles, name='Verified'))
            await inter.send('✅')  # Check mark
        else:  # You didn't meet the time :(
            await inter.send(
                'You don\'t qualify to be verified yet! Check back 24 hours after you join.'
            )

    @nextcord.slash_command()
    async def time(
        self,
        inter: nextcord.Interaction,
        org_time: str = nextcord.SlashOption(
            required=True, description="The time to convert"),
        org_zone: str = nextcord.SlashOption(required=True,
                                             description="Original timezone"),
        new_zone: str = nextcord.SlashOption(required=True,
                                             description="New timezone")):
        """Converts times between timezones. For a list of zones see: https://is.gd/4Q98XQ"""
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

        new_zone = convert_tz(new_zone)
        org_zone = convert_tz(org_zone)
        try:
            utime = datetime.strptime(org_time, tformat)
            utime = datetime.combine(date=datetime.today(), time=utime.time())
        except ValueError:
            await inter.send('Couldn\'t parse that time, see `,help time`')
            return

        org_time = datetime.strftime(utime, tformat)
        ntime = datetime.strftime(utime.astimezone(new_zone), tformat)
        await inter.send(f"{org_time} {org_zone} is {ntime} {new_zone}")
