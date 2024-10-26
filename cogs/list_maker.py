"""
https://github.com/vpaone59
"""

import discord
from discord import app_commands
from discord.ext import commands
from logging_config import create_new_logger
from db_helper import get_db_connection

logger = create_new_logger(__name__)


class ListMaker(commands.Cog):
    """
    This Cog will allow users to create and manage custom lists
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @app_commands.command(
        name="create_list",
        description="Create a custom list that only you can add items to",
    )
    async def create_user_list(self, interaction: discord.Interaction, list_name: str):
        """
        User creates a new list

        Save list to DB with user_id and list_name in the lists table
        """
        # Grab the user's ID from the interaction
        user_id = interaction.user.id

        # Get a connection to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the list already exists
        if self.does_list_exist(user_id, list_name):
            await interaction.response.send_message(
                f'List "{list_name}" already exists.'
            )
            return

        # Create the list
        try:
            cursor.execute(
                "INSERT INTO lists (user_id, list_name) VALUES (?, ?)",
                (user_id, list_name),
            )
            conn.commit()
            await interaction.response.send_message(f'List "{list_name}" created.')
        except Exception as e:
            await interaction.response.send_message(
                f'Failed to create list "{list_name}": {e}'
            )
        finally:
            conn.close()

    @app_commands.command(name="add_item_to_list", description="Add an item to a list")
    async def add_item_to_list(
        self, interaction: discord.Interaction, list_name: str, item_name: str
    ):
        """
        Add an item to a list

        Save item to DB with user_id, list_name, and item_name in the items table
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO list_items (user_id, list_name, item_name) VALUES (?, ?, ?)",
                (interaction.author.id, list_name, item),
            )
            conn.commit()
            await interaction.send(f'Item "{item}" added to list "{list_name}"')
        except Exception as e:
            await interaction.send(
                f'Failed to add item "{item}" to list "{list_name}": {e}'
            )

    @app_commands.command(
        name="remove_item_from_list", description="Remove an item from a list"
    )
    async def remove_item_from_list(
        self, interaction: discord.Interaction, list_name: str, item: str
    ):
        """
        Remove an item from a list

        Delete item from items table
        """
        pass

    def get_user_list_items(self, user_id, list_name: str):
        """
        Get all list items for a user's list

        Returns a list of tuples with the item names
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT item_name FROM list_items WHERE user_id = ? AND list_name = ?",
                (user_id, list_name),
            )
            result = cursor.fetchall()
            print(result)
            return result
        except Exception as e:
            logger.error("Failed to get list items: %s", e)
            return

    def does_list_exist(self, user_id, list_name: str):
        """
        Check if a list already exists in the database
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the list name already exists for the user
            cursor.execute(
                "SELECT 1 FROM lists WHERE user_id = ? AND list_name = ?",
                (user_id, list_name),
            )
            result = cursor.fetchone()
            return bool(result)

        except Exception as e:
            logger.error("Failed to check if list exists: %s", e)
            return False


async def setup(bot):
    await bot.add_cog(ListMaker(bot))
