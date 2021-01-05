import discord
from discord.ext import commands


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx, command="help"):
        if command == "help":
            help_embed = discord.Embed(
                title="Help",
                description="For more info on a catgeory run `help [category]`",
                color=discord.Color.blurple
            )
            help_embed.add_field(name="Trivia", value="An RA themed competivie trivia game, with a scoreboard.")
            help_embed.add_field(name="Utility", value="Utility Commands")
            return await ctx.send(embed=help_embed)

        elif command == "trivia":
            trivia_embed = discord.Embed(
                title="Trivia Commands",
                description="Help With Trivia Commands",
                color=discord.Color.dark_gold
            )
            trivia_embed.add_field(name="trivia start", value="Starts a new game in the current channel")
            trivia_embed.add_field(name="trivia stats", value="Returns your trivia win/loss statistics")
            trivia_embed.add_field(name='trivia top', value="Sends an embed with the top 5 ranked users in trivia")
            return await ctx.send(embed=trivia_embed)

        elif command == 'utils':
            util_embed = discord.Embed(
                title='Utility Commands',
                description="Utility Commands",
                color=discord.Color.darker_grey
            )
            util_embed.add_field(name="bofh", value="Convenient solutions to inconvenient tech problems")
            util_embed.add_field(name="info", value="Information about the bot instance")
            util_embed.add_field(name="ping", value="Displays latency between the client and the bot")
            util_embed.add_field(name="roll", value="Rolls dice")
            util_embed.add_field(name="userinfo", value="Displays information abouyt users")
            util_embed.add_field(name="verify", value="Add yourself to the verified user role if the server, if you qualify.")
            return await ctx.send(embed=util_embed)
