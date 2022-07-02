from nextcord.ext import commands
import nextcord, logging


class Roles(commands.Cog):

    def __init__(self, bot, db, cur):
        self.bot = bot
        self.db = db
        self.cur = cur

    # Helpers
    async def send_message(self):
        """Generates or updates the roles message and puts the content in the
        configured channel"""
        msg = 'React with one of the emotes below to be given the indicated vanity role:\n'
        for role in self.cur.execute(
                'SELECT name, emoji from roles ORDER BY name'):
            msg += f"{role[1]} - `{role[0]}`\n"  # EMOJI - `ROLENAME`
        chan = self.bot.get_channel(int(self.bot.getConfig('Roles',
                                                           'channel')))
        if chan is not None:  # There is a channel set, right?
            #  Did we send the last message (Old role message)? Then edit it
            try:
                last_msg = await chan.fetch_message(
                    chan.last_message_id)  # Docs say to do it this way
            except (nextcord.NotFound, nextcord.errors.HTTPException):
                last_msg = None
            if last_msg is not None and last_msg.author == self.bot.user:
                await last_msg.edit(content=msg)
            else:  # Otherwise, send a new message
                await chan.send(content=msg)

    @commands.command(usage="#somechannel")
    @commands.has_permissions(manage_roles=True)
    async def rolechan(self, ctx):
        """Sets the channel in which the bot posts the role message"""
        chan = ctx.message.channel_mentions[0]
        if chan.id == self.bot.getConfig('Roles', 'channel'):
            return
        self.bot.setConfig('Roles', 'channel', str(chan.id))
        await self.send_message()
        await ctx.send('Channel set!')

    @commands.command(usage='@somerole')
    @commands.has_permissions(manage_roles=True)
    async def roleset(self, ctx, role: nextcord.Role):
        """Assigns an emoji to a reaction role"""
        rolechan = self.bot.getConfig('Roles', 'channel')
        # A message can only have 20 reacts, so limit to the first 20 letters
        if not rolechan or self.cur.execute(
                'SELECT Count(*) FROM roles').fetchone()[0] > 19:
            await ctx.send(
                'The role channel does not exist, or has too many roles!')
            return
        prompt = await ctx.send(
            'React to this message with an emoji for the role')

        def check(reaction, user):
            # Make sure the react was to the prompt message by the same user
            return reaction.message == prompt and user.id == ctx.author.id

        react, _user = await self.bot.wait_for('reaction_add',
                                               timeout=60.0,
                                               check=check)
        # Insert, or replace if it already exists
        self.cur.execute(
            'INSERT INTO roles (name, emoji) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET name=excluded.name, emoji=excluded.emoji',
            (role.name, str(react)))
        self.db.commit()
        await self.send_message()
        await ctx.send('Role set!')

    @commands.command(usage='@somerole')
    @commands.has_permissions(manage_roles=True)
    async def rolerm(self, ctx, role: nextcord.Role):
        """Removes a role from the reaction roles list"""
        self.cur.execute('DELETE FROM roles WHERE name=?', (role.name, ))
        self.db.commit()
        await self.send_message()
        await ctx.send('Role removed')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Is the react from the role channel?
        if payload.channel_id == int(self.bot.getConfig('Roles', 'channel')):
            channel = self.bot.get_channel(payload.channel_id)
            guild = self.bot.get_guild(payload.guild_id)
            # Is it the last message in the channel?
            if payload.message_id == channel.last_message_id:
                entry = self.cur.execute('SELECT * FROM roles where emoji=?',
                                         (str(payload.emoji), )).fetchone()
                try:
                    role = nextcord.utils.get(guild.roles, name=entry[0])
                except TypeError:
                    logging.error(
                        'User attempted add role/react which was not found, ignoring'
                    )
                    return
                await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # Is the react from the role channel?
        if payload.channel_id == int(self.bot.getConfig('Roles', 'channel')):
            channel = self.bot.get_channel(payload.channel_id)
            guild = self.bot.get_guild(payload.guild_id)
            # Is it the last message in the channel?
            if payload.message_id == channel.last_message_id:
                entry = self.cur.execute('SELECT * FROM roles where emoji=?',
                                         (str(payload.emoji), )).fetchone()
                role = nextcord.utils.get(guild.roles, name=entry[0])
                if not role:
                    logging.error(
                        'User attempted to remove role %s which was not found, ignoring',
                        entry[1])
                    return
                # playload.member doesn't work for remove
                await self.bot.get_guild(payload.guild_id
                                         ).get_member(payload.user_id
                                                      ).remove_roles(role)
