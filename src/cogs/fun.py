import nextcord, random
from nextcord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()
    async def bofh(self, inter: nextcord.Interaction):
        """Convenient solutions to inconvenient tech problems"""
        # https://stackoverflow.com/questions/14924721/how-to-choose-a-random-line-from-a-text-file#14924739
        line_num = 0
        selected = ""
        with open("data/excuses.txt") as f:
            while 1:
                line = f.readline()
                if not line:
                    break
                line_num += 1
                if random.uniform(0, line_num) < 1:
                    selected = line
        await inter.send(selected.strip())

    @nextcord.slash_command()
    async def roll(self,
                   inter: nextcord.Interaction,
                   roll: str = nextcord.SlashOption(
                       description="NUMdSIDE dice to roll", default="1d6")):
        """Rolls a dice"""
        embed = nextcord.Embed(title="Dice Rolls")
        try:
            sides = int(roll.split("d")[1])
            rolls = int(roll.split("d")[0])
        except Exception:
            await inter.send(
                "Wrong format, the commands format is `[number of rolls]d[number of sides]` eg.(1d5, or 10d45)"
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
        await inter.send(embed=embed)
