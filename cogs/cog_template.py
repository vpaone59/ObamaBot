"""
https://github.com/vpaone59
"""

from discord.ext import commands


class COG_NAME(commands.Cog):
    """ 
    Class
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        print(f'{self} ready')


async def setup(bot):
    await bot.add_cog(COG_NAME(bot))
