"""
https://github.com/vpaone59
"""

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
        logger.info("%s ready", self)

    @commands.command(name="create_list")
    async def create_list(self, ctx, *list_name: str):
        """
        Create a new list
        """
        user_id = ctx.author.id
        print("user_id", user_id)
        print("list_name", list_name)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO lists (user_id, list_name) VALUES (?, ?)",
                (user_id, list_name),
            )
            conn.commit()
            await ctx.send(f'List "{list_name}" created.')
        except Exception as e:
            await ctx.send(f'Failed to create list "{list_name}": {e}')
        finally:
            conn.close()

    @commands.command(name="add_item")
    async def add_item(self, ctx, list_name: str, *, item: str):
        """
        Add an item to a list
        """
        pass

    @commands.command(name="remove_item")
    async def remove_item(self, ctx, list_name: str, *, item: str):
        """
        Remove an item from a list
        """
        pass

    @commands.command(name="show_list")
    async def show_list(self, ctx, list_name: str):
        """
        Display the list
        """
        pass

    @commands.command(name="show_all_lists")
    async def show_all_lists(self, ctx):
        """
        Display all lists for the user
        """
        pass


async def setup(bot):
    await bot.add_cog(ListMaker(bot))
