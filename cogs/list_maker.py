"""
https://github.com/vpaone59
"""

from discord.ext import commands


class ListMaker(commands.Cog):
    """
    Class for managing user lists
    """

    def __init__(self, bot):
        self.bot = bot
        self.user_lists = {}  # Dictionary to store user lists

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        print(f"{self.__class__.__name__} cog has been loaded")

    @commands.command(name="create_list")
    async def create_list(self, ctx, list_name: str):
        """
        Create a new list for the user
        """
        user_id = ctx.author.id
        if user_id not in self.user_lists:
            self.user_lists[user_id] = {}
        if list_name in self.user_lists[user_id]:
            await ctx.send(f"You already have a list named '{list_name}'.")
        else:
            self.user_lists[user_id][list_name] = []
            await ctx.send(f"List '{list_name}' created.")

    @commands.command(name="add_to_list")
    async def add_to_list(self, ctx, list_name: str, *, item: str):
        """
        Add an item to an existing list
        """
        user_id = ctx.author.id
        if user_id in self.user_lists and list_name in self.user_lists[user_id]:
            self.user_lists[user_id][list_name].append(item)
            await ctx.send(f"Added '{item}' to list '{list_name}'.")
        else:
            await ctx.send(f"List '{list_name}' does not exist.")

    @commands.command(name="view_list")
    async def view_list(self, ctx, list_name: str):
        """
        View the items in a list
        """
        user_id = ctx.author.id
        if user_id in self.user_lists and list_name in self.user_lists[user_id]:
            items = self.user_lists[user_id][list_name]
            if items:
                await ctx.send(f"Items in '{list_name}':\n" + "\n".join(items))
            else:
                await ctx.send(f"List '{list_name}' is empty.")
        else:
            await ctx.send(f"List '{list_name}' does not exist.")

    @commands.command(name="delete_list")
    async def delete_list(self, ctx, list_name: str):
        """
        Delete an existing list
        """
        user_id = ctx.author.id
        if user_id in self.user_lists and list_name in self.user_lists[user_id]:
            del self.user_lists[user_id][list_name]
            await ctx.send(f"List '{list_name}' deleted.")
        else:
            await ctx.send(f"List '{list_name}' does not exist.")


async def setup(bot):
    await bot.add_cog(ListMaker(bot))
