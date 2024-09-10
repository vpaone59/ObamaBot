"""
https://github.com/vpaone59
"""

from discord.ext import commands


class ListMaker(commands.Cog):
    """
    This Cog will allow users to create and manage custom lists
    """

    def __init__(self, bot):
        self.bot = bot
        self.user_lists = {}  # Dictionary to store user lists

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded`
        """
        print(f"{self.__class__.__name__} loaded")

    @commands.command(name="create_list")
    async def create_list(self, ctx, list_name: str):
        """Create a new list"""
        user_id = ctx.author.id
        if user_id not in self.user_lists:
            self.user_lists[user_id] = {}
        self.user_lists[user_id][list_name] = []
        await ctx.send(f'List "{list_name}" created.')

    @commands.command(name="add_item")
    async def add_item(self, ctx, list_name: str, *, item: str):
        """Add an item to a list"""
        user_id = ctx.author.id
        if user_id in self.user_lists and list_name in self.user_lists[user_id]:
            self.user_lists[user_id][list_name].append(item)
            await ctx.send(f'Item "{item}" added to list "{list_name}".')
        else:
            await ctx.send(f'List "{list_name}" does not exist.')

    @commands.command(name="remove_item")
    async def remove_item(self, ctx, list_name: str, *, item: str):
        """Remove an item from a list"""
        user_id = ctx.author.id
        if user_id in self.user_lists and list_name in self.user_lists[user_id]:
            try:
                self.user_lists[user_id][list_name].remove(item)
                await ctx.send(f'Item "{item}" removed from list "{list_name}".')
            except ValueError:
                await ctx.send(f'Item "{item}" not found in list "{list_name}".')
        else:
            await ctx.send(f'List "{list_name}" does not exist.')

    @commands.command(name="show_list")
    async def show_list(self, ctx, list_name: str):
        """Display the list"""
        user_id = ctx.author.id
        if user_id in self.user_lists and list_name in self.user_lists[user_id]:
            items = self.user_lists[user_id][list_name]
            if items:
                await ctx.send(f'List "{list_name}": {", ".join(items)}')
            else:
                await ctx.send(f'List "{list_name}" is empty.')
        else:
            await ctx.send(f'List "{list_name}" does not exist.')


async def setup(bot):
    await bot.add_cog(ListMaker(bot))
