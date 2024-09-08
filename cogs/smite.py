"""
Custom Smite Cog commands for ObamaBot https://github.com/vpaone59
"""

import random
import json
import discord
from discord import app_commands
from discord.ext import commands
from logging_config import create_new_logger

logger = create_new_logger(__name__)

with open("./dynamic/smite_gods.json", "r", encoding="utf-8") as file:
    god_list = json.load(file)

smite_god_class_list = ["mage", "warrior", "assassin", "guardian", "hunter"]


class SmiteShuffler(commands.Cog):
    """
    Smite Shuffler Cog for ObamaBot

    This is also an example of how to use Slash commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self)

    @commands.command(description="Syncs the Smite.py Cog to Discord")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def sync_smite(self, ctx) -> None:
        """
        Specifically sync the slash commands from this Cog
        """
        number_of_synced_commands = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(number_of_synced_commands)} commands.")

    @commands.command(aliases=["gods"])
    async def get_all_gods(self, ctx):
        """
        List all current Gods
        """
        count = 0
        god_list_length = len(god_list["gods"])
        list_text = ""

        for god in god_list["gods"]:
            god_name = god["name"]
            if count == god_list_length - 1:
                list_text += f"{god_name}."
            else:
                list_text += f"{god_name}, "
            count += 1
        await ctx.send(list_text)

    @commands.command(aliases=["ss"])
    async def get_random_god(self, ctx, god_type: str = None):
        """
        Chooses a random God. Optionally takes a god type to filter return
        """
        if god_type is None:
            shuffle_gods = god_list["gods"]
        else:
            if god_type.lower() not in smite_god_class_list:
                await ctx.send(f"{god_type} is not one of {smite_god_class_list}")
                return
            else:
                shuffle_gods = [
                    god
                    for god in god_list["gods"]
                    if god["type"].lower() == god_type.lower()
                ]

        random_god = random.choice(shuffle_gods)
        random_god_name = random_god["name"]
        await ctx.send(f"{random_god_name}")

    @app_commands.command(name="add_god", description="Add a God to the God list")
    @commands.has_permissions(administrator=True)
    async def add_god(
        self,
        interaction: discord.Interaction,
        god_name: str,
        god_pantheon: str,
        god_type: str,
    ):
        """
        Add a God to the God list
        """
        if god_type.lower() not in smite_god_class_list:
            await interaction.response.send_message(
                f"{god_type} is not one of {smite_god_class_list}"
            )
        else:
            response = add_god_to_list(god_name, god_type, god_pantheon)
            await interaction.response.send_message(f"{response}")

    @app_commands.command(
        name="remove_god", description="Remove a God from the God list"
    )
    @commands.has_permissions(administrator=True)
    async def remove_god(self, interaction: discord.Interaction, god_name: str):
        """
        Remove a God from the God list
        """
        response = remove_god_from_list(god_name)
        await interaction.response.send_message(f"{response}")


def add_god_to_list(name, type, pantheon):
    """
    Function that adds a new God to the God list with a name, type and pantheon parameter
    """
    # Capitalize the first letter of each String in each parameter
    # "god name" will become "God Name"
    name = " ".join(word.capitalize() for word in name.split())
    pantheon = " ".join(word.capitalize() for word in pantheon.split())
    type = " ".join(word.capitalize() for word in type.split())

    for god in god_list["gods"]:
        if god["name"] == name:
            return f"The God {name} already exists."

    new_god = {"name": name, "pantheon": pantheon, "type": type}
    try:
        # Append the new God to the list of Gods
        god_list["gods"].append(new_god)
        god_list["gods"].sort(key=lambda x: x["name"])
        # Write the data to the file
        with open("./dynamic/smite_gods.json", "w", encoding="utf-8") as file:
            json.dump(god_list, file, indent=4)
        return f"```God Added\n---\nName: {name}\nPantheon: {pantheon}\nType: {type}```"
    except Exception as e:
        return f"ERROR : {e}"


def remove_god_from_list(name):
    """
    Function that removes a god from the God list by name and updates the JSON file
    """
    capitalized_name = " ".join(word.capitalize() for word in name.split())
    index = -1

    # Get the index of the name
    for curr_index, god in enumerate(god_list["gods"]):
        if god["name"] == capitalized_name:
            index = curr_index
            break

    if index != -1:
        try:
            removed_god = god_list["gods"].pop(index)

            with open("./dynamic/smite_gods.json", "w", encoding="utf-8") as file:
                json.dump(god_list, file, indent=4)

            return f"```God Removed\n---\nName: {removed_god['name']}\nPantheon: {removed_god['pantheon']}\nType: {removed_god['type']}```"
        except Exception as e:
            return f"ERROR : {e}"
    else:
        return f"'{name}' does not exist in the list."


def god_check(name):
    """
    Checks to see if the input name exists within the God list
    """
    # Capitalize the name so it can properly check against the formatted names already in the list
    capitalized_name = " ".join(word.capitalize() for word in name.split())
    for god in god_list["gods"]:
        if god["name"] == capitalized_name:
            return True
    return False


async def setup(bot):
    await bot.add_cog(
        SmiteShuffler(bot), guilds=[discord.Object(id=1040708391921786901)]
    )
