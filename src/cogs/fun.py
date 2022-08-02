import nextcord, random, sys
from nextcord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()
    async def bofh(self, inter: nextcord.Interaction):
        """Convenient solutions to inconvenient tech problems"""
        # Wow that was really overcomplicated.
        lines = open('data/excuses.txt').read().splitlines() # Open file and split lines into a list
        line = random.choice(lines) # Choose a random line from the list
        await inter.send(str(line)) # Send the line

    @nextcord.slash_command()
    async def roll(self,
                   inter: nextcord.Interaction,
                   sides: int = nextcord.SlashOption(default=6, description="Number of sides on the dice"),
                   rolls: int = nextcord.SlashOption(default=1, description="Times to roll the dice")):
        """Rolls a dice"""
        if rolls > 0 and rolls <= 32:
            if sides > 0 and sides <= sys.maxsize:
                embed = nextcord.Embed(title="Dice Rolls")
                for i in range(rolls):
                    embed.add_field(name=f"Roll {i+1}", value=random.randint(1, sides))
                await inter.send(embed=embed)
            else:
                await inter.send(f"Sides cannot be less than 1 or exceed {sys.maxsize}")
        else:
            await inter.send("Rolls cannot be less than 1 or exceed 32")