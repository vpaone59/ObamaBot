import discord
from discord import app_commands
from discord.ext import commands
import random
import json

with open("./dynamic/smite_gods.json", "r") as file:
    god_list = json.load(file)

available_types = ['mage', 'warrior', 'assassin', 'guardian', 'hunter']


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
    async def gods(self, ctx):
        """
        List all current Gods
        """
        count = 0
        god_list_length = len(god_list["gods"])
        list_text = ""

        for god in god_list["gods"]:
            god_name = god["name"]
            if count == god_list_length-1:
                list_text += f"{god_name}."
            else:
                list_text += f"{god_name}, "
            count += 1
        await ctx.send(list_text)

    @commands.command()
    async def shuffle(self, ctx, god_type: str = None):
        """
        Chooses a random God. Optionally takes a god_type filter results
        """
        if god_type is None:
            shuffle_gods = god_list["gods"]
        else:
            if god_type.lower() not in available_types:
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
    async def add_god(self, interaction: discord.Interaction, god_name: str, god_pantheon: str, god_type: str):
        """
        Add a God to the God list
        """
        print(god_name, god_pantheon, god_type)
        if god_type.lower() not in available_types:
            await interaction.response.send_message(f"{god_type} is not one of {available_types}")
        else:
            response = add_god_to_list(god_name, god_type, god_pantheon)
            await interaction.response.send_message(f'{response}')


def remove_god_from_list(name):
    pass


def add_god_to_list(name, type, pantheon):
    """
    Function that adds a new God to the God list with a name, type and pantheon parameter
    """
    # Capitalize the first letter of each String in each parameter
    # "god name" will become "God Name"
    name = ' '.join(word.capitalize() for word in name.split())
    pantheon = ' '.join(word.capitalize() for word in pantheon.split())
    type = ' '.join(word.capitalize() for word in type.split())

    for god in god_list["gods"]:
        if god["name"] == name:
            return f"The God {name} already exists."

    new_god = {
        "name": name,
        "pantheon": pantheon,
        "type": type
    }
    try:
        # Append the new God to the list of Gods
        god_list["gods"].append(new_god)
        god_list["gods"].sort(key=lambda x: x["name"])
        # Write the data to the file
        with open("./dynamic/smite_gods.json", "w") as file:
            json.dump(god_list, file, indent=4)
            print("done")
        return f"```God Added\n---\nName: {name}\nPantheon: {pantheon}\nType: {type}```"
    except Exception as e:
        return f"ERROR : {e}"


async def setup(bot):
    await bot.add_cog(Smite_Shuffler(bot), guilds=[discord.Object(id=1040708391921786901)])
