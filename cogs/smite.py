import discord
from discord import app_commands
from discord.ext import commands
import random
import json

with open("./dynamic/smite_gods.json", "r") as file:
    god_list = json.load(file)

god_list_length = len(god_list["gods"])
available_types = ['mage', 'warrior', 'asassin', 'guardian', 'hunter']


class Smite_Shuffler(commands.Cog):
    """
    Smite Shuffler Cog for ObamaBot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} ready')

    @commands.command()
    async def sync_smite(self, ctx) -> None:
        """
        Specifically sync the slash commands from this Cog
        """
        number_of_synced_commands = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced {len(number_of_synced_commands)} commands.')

    @commands.command()
    async def shuffle(self, ctx, god_type: str = None):
        """
        Chooses a random God. Optionally takes a god_type filter results
        """
        if god_type is None:
            shuffle_gods = god_list["gods"]
        else:
            if god_type not in available_types:
                await ctx.send(f'{god_type} is not one of {available_types}')
                return
            else:
                shuffle_gods = [god for god in god_list["gods"]
                                if god["type"].lower() == god_type.lower()]

        random_god = random.choice(shuffle_gods)
        random_god_name = random_god["name"]
        await ctx.send(f"{random_god_name}")

    @app_commands.command(name="add_god", description="add a god")
    @commands.has_permissions(administrator=True)
    async def add_god(self, interaction: discord.Interaction, god_name: str, god_type: str):
        """
        Add a God to the God list
        """
        if god_type not in available_types:
            await interaction.response.send_message(f"{god_type} is not one of {available_types}")
        await interaction.response.send_message(f'Thanks {god_name} {god_type}')

    @commands.command()
    async def gods(self, ctx):
        """
        List all current Gods
        """
        count = 0
        god_list_text = ""

        for god in god_list["gods"]:
            god_name = god["name"]
            if count == god_list_length-1:
                god_list_text += f"{god_name}."
            else:
                god_list_text += f"{god_name}, "
            count += 1
        await ctx.send(god_list_text)


async def setup(bot):
    await bot.add_cog(Smite_Shuffler(bot), guilds=[discord.Object(id=1040708391921786901)])
