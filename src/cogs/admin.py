from nextcord.ext import commands
import nextcord, asyncio


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Create polls using embeds and reactions',
                      usage="\"question\" \"answers 1-9\"")
    @commands.has_permissions(manage_messages=True)
    # Only people who can manage messages can use this
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

        embed = nextcord.Embed(
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

    @commands.command(help='Bans a user from the server', usage='@someone')
    @commands.has_permissions(ban_members=True)
    async def kb(self, ctx):
        user = ctx.message.mentions[0]  # Get the first mentioned user
        await ctx.guild.ban(user, reason=f"Banned via command by {ctx.author}")

    @commands.command(help="Kicks a mentioned user from the server",
                      usage="@someone")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx):
        if ctx.message.mentions[0] is not None:
            user = ctx.message.mentions[0]
            await ctx.guild.kick(user,
                                 reason=f"Kicked via command by {ctx.author}")

    @commands.command(help='Mass-deletes messages in the current channel',
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
